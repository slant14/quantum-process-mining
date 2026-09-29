#!/usr/bin/env python3
"""Build the qcompiler-mining input circuit corpus from MQT Bench.

Level: INDEP (target-independent), opt_level=0 so that Qiskit's optimiser is
NOT baked into the corpus. The corpus is toolchain-neutral: Qiskit is only the
generator, every file is plain OpenQASM.
"""
from __future__ import annotations

import csv
import hashlib
import json
import multiprocessing as mp
import platform
import subprocess
import sys
import time
from pathlib import Path

from mqt.bench import BenchmarkLevel, get_benchmark
from mqt.bench.benchmarks import get_available_benchmark_names, get_benchmark_description
from qiskit import qasm2, qasm3

OUT = Path("/mnt/user-data/outputs/qcm-corpus-v1")
LEVEL = "indep"
OPT_LEVEL = 0
SEED = 42
TIMEOUT_S = 45
MEM_CAP_BYTES = 1_600_000_000
SIZES = [2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 20, 24, 32]
# Oracle/arithmetic circuits whose construction blows up; capped so the ladder
# stays affordable. The cap is recorded in provenance.json.
SIZE_CAP = {"grover": 12, "qwalk": 12, "shor": 20, "hhl": 10,
            "multiplier": 12, "hrs_cumulative_multiplier": 12,
            "rg_qft_multiplier": 12, "bmw_quark_copula": 12}

# ---------------------------------------------------------------- taxonomy --
# stress_class: which part of a compiler pipeline the circuit exercises.
STRESS = {
    "ghz": "entangling-structure", "ghz_dynamic": "dynamic-control",
    "wstate": "entangling-structure", "graphstate": "routing-stress",
    "qft": "canonical-dense", "qftentangled": "canonical-dense",
    "dynamic_qft": "dynamic-control", "dj": "oracle-shallow",
    "bv": "oracle-shallow", "grover": "oracle-decomposition",
    "qwalk": "oracle-decomposition", "ae": "canonical-composite",
    "qpeexact": "canonical-composite", "qpeinexact": "canonical-composite",
    "iqpe": "dynamic-control", "hhl": "canonical-composite",
    "shor": "depth-stress", "vqe_real_amp": "variational",
    "vqe_su2": "variational", "vqe_two_local": "variational",
    "qaoa": "variational", "qnn": "variational",
    "randomcircuit": "unstructured-control",
    "cdkm_ripple_carry_adder": "arithmetic-synthesis",
    "vbe_ripple_carry_adder": "arithmetic-synthesis",
    "draper_qft_adder": "arithmetic-synthesis",
    "half_adder": "arithmetic-synthesis", "full_adder": "arithmetic-synthesis",
    "modular_adder": "arithmetic-synthesis", "multiplier": "arithmetic-synthesis",
    "rg_qft_multiplier": "arithmetic-synthesis",
    "hrs_cumulative_multiplier": "arithmetic-synthesis",
    "seven_qubit_steane_code": "fault-tolerant",
    "shors_nine_qubit_code": "fault-tolerant",
    "bmw_quark_cardinality": "industry-workload",
    "bmw_quark_copula": "industry-workload",
}

# CORE: documented subset spanning every stress class; the headline
# cross-toolchain comparison runs on these. Everything else is EXTENDED.
CORE = {
    "ghz", "wstate", "graphstate", "qft", "qpeexact", "dj", "grover", "ae",
    "qwalk", "vqe_two_local", "vqe_su2", "qaoa", "qnn", "randomcircuit",
    "cdkm_ripple_carry_adder", "shor",
}
# Dynamic-control circuits: OpenQASM 3 only, never QASM 2 -> Tier B by nature.
DYNAMIC = {"dynamic_qft", "ghz_dynamic", "iqpe"}


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def _worker(name: str, size: int, q: mp.Queue) -> None:
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (MEM_CAP_BYTES, MEM_CAP_BYTES))
    try:
        try:
            qc = get_benchmark(name, BenchmarkLevel.INDEP, size,
                               opt_level=OPT_LEVEL, seed=SEED)
            seeded = True
        except TypeError:
            qc = get_benchmark(name, BenchmarkLevel.INDEP, size,
                               opt_level=OPT_LEVEL)
            seeded = False
        try:
            s2, e2 = qasm2.dumps(qc), ""
        except Exception as exc:
            s2, e2 = "", type(exc).__name__
        try:
            s3, e3 = qasm3.dumps(qc), ""
        except Exception as exc:
            s3, e3 = "", type(exc).__name__
        ops = {k: int(v) for k, v in qc.count_ops().items()}
        two_q = sum(1 for ins in qc.data if len(ins.qubits) == 2)
        multi_q = sum(1 for ins in qc.data if len(ins.qubits) > 2)
        q.put({
            "ok": True, "seeded": seeded, "num_qubits": qc.num_qubits,
            "num_clbits": qc.num_clbits, "depth": qc.depth(), "size": qc.size(),
            "two_qubit_gates": two_q, "multi_qubit_gates": multi_q,
            "ops": ops, "qasm2": s2, "qasm3": s3, "qasm2_err": e2,
            "qasm3_err": e3,
        })
    except Exception as exc:  # generation itself failed
        q.put({"ok": False, "error": f"{type(exc).__name__}: {str(exc)[:160]}"})


def generate(name: str, size: int) -> dict:
    q: mp.Queue = mp.Queue()
    p = mp.Process(target=_worker, args=(name, size, q))
    t0 = time.time()
    p.start()
    p.join(TIMEOUT_S)
    if p.is_alive():
        p.terminate()
        p.join()
        return {"ok": False, "error": f"Timeout>{TIMEOUT_S}s", "secs": time.time() - t0}
    res = q.get() if not q.empty() else {"ok": False, "error": "NoResult"}
    res["secs"] = round(time.time() - t0, 3)
    return res



STATE = Path("/home/claude/corpus_state.jsonl")


def tasks() -> list[tuple[str, int]]:
    out = []
    for name in sorted(get_available_benchmark_names()):
        cap = SIZE_CAP.get(name, 10 ** 9)
        for size in SIZES:
            if size <= cap:
                out.append((name, size))
    return out


def run_pending(budget_s: float) -> None:
    """Generate circuits until the time budget runs out. Resumable."""
    done = set()
    if STATE.exists():
        for line in STATE.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                done.add((r["algorithm"], r["requested_size"]))
    t0 = time.time()
    with STATE.open("a") as fh:
        for name, size in tasks():
            if (name, size) in done:
                continue
            if time.time() - t0 > budget_s:
                break
            r = generate(name, size)
            rec = {"algorithm": name, "requested_size": size, "secs": r["secs"]}
            if r["ok"]:
                rec.update({k: r[k] for k in (
                    "seeded", "num_qubits", "num_clbits", "depth", "size",
                    "two_qubit_gates", "multi_qubit_gates", "ops", "qasm2",
                    "qasm3", "qasm2_err", "qasm3_err")})
                rec["ok"] = True
            else:
                rec.update({"ok": False, "error": r.get("error", "?")})
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            tag = "OK " if r["ok"] else "SKIP"
            print(f"{tag} {name}_n{size:03d} {r['secs']:.1f}s", flush=True)
    pend = len([t for t in tasks() if t not in done])
    print(f"-- budget spent; ~{pend} tasks were pending at start", flush=True)


def materialise() -> None:
    """Turn the state file into the on-disk corpus + manifest."""
    (OUT / "qasm2").mkdir(parents=True, exist_ok=True)
    (OUT / "qasm3").mkdir(parents=True, exist_ok=True)
    rows, skipped, seen = [], [], set()
    uid = 0
    for line in STATE.read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        name, size = r["algorithm"], r["requested_size"]
        if not r["ok"]:
            skipped.append({"algorithm": name, "requested_size": size,
                            "reason": r.get("error", "?"), "secs": r["secs"]})
            continue
        nq = r["num_qubits"]
        if (name, nq) in seen:
            continue
        seen.add((name, nq))
        uid += 1
        lvl = r.get("level", LEVEL)
        stem = f"{name}_{lvl}_n{nq:03d}"
        p2 = p3 = ""
        if r["qasm2"]:
            d = OUT / "qasm2" / name
            d.mkdir(parents=True, exist_ok=True)
            (d / f"{stem}.qasm").write_text(r["qasm2"])
            p2 = f"qasm2/{name}/{stem}.qasm"
        if r["qasm3"]:
            d = OUT / "qasm3" / name
            d.mkdir(parents=True, exist_ok=True)
            (d / f"{stem}.qasm").write_text(r["qasm3"])
            p3 = f"qasm3/{name}/{stem}.qasm"
        rows.append({
            "corpus_uid": f"QCM-C-{uid:04d}", "circuit_id": stem,
            "algorithm": name, "description": get_benchmark_description(name),
            "stress_class": STRESS.get(name, "unclassified"),
            "selection_tier": "CORE" if name in CORE else "EXTENDED",
            "portability_tier": "A" if p2 else "B",
            "level": lvl, "opt_level": OPT_LEVEL if lvl == LEVEL else "n/a",
            "seeded": r["seeded"],
            "seed": SEED if r["seeded"] else "", "requested_size": size,
            "num_qubits": nq, "num_clbits": r["num_clbits"], "depth": r["depth"],
            "num_instructions": r["size"],
            "two_qubit_gates": r["two_qubit_gates"],
            "multi_qubit_gates": r["multi_qubit_gates"],
            "has_dynamic_control": bool(name in DYNAMIC or "if_else" in r["ops"]),
            "ops_histogram": json.dumps(r["ops"], sort_keys=True),
            "qasm2_path": p2, "qasm3_path": p3,
            "qasm2_error": r["qasm2_err"], "qasm3_error": r["qasm3_err"],
            "sha256_16_qasm2": _sha(r["qasm2"]) if r["qasm2"] else "",
            "sha256_16_qasm3": _sha(r["qasm3"]) if r["qasm3"] else "",
            "gen_seconds": r["secs"],
        })
    rows.sort(key=lambda x: (x["algorithm"], x["num_qubits"]))
    for i, row in enumerate(rows, 1):
        row["corpus_uid"] = f"QCM-C-{i:04d}"
    with (OUT / "manifest.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    with (OUT / "generation_log.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["algorithm", "requested_size", "reason", "secs"])
        w.writeheader(); w.writerows(skipped)

    import qiskit
    prov = {
        "corpus": "qcompiler-mining input circuit corpus", "version": "v1",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": "MQT Bench (Quetschlich, Burgholzer, Wille; Quantum 7:1062, 2023)",
        "level": "BenchmarkLevel.INDEP (target-independent)",
        "opt_level": OPT_LEVEL, "seed": SEED, "size_ladder": SIZES,
        "size_caps": SIZE_CAP, "timeout_seconds": TIMEOUT_S,
        "worker_memory_cap_bytes": MEM_CAP_BYTES,
        "mqt_bench_version": subprocess.run(
            [sys.executable, "-m", "pip", "show", "mqt.bench"],
            capture_output=True, text=True).stdout.split("Version:")[1].split("\n")[0].strip(),
        "qiskit_version": qiskit.__version__, "python": sys.version.split()[0],
        "platform": platform.platform(), "n_circuits": len(rows),
        "n_tier_a_qasm2": sum(1 for r in rows if r["portability_tier"] == "A"),
        "n_tier_b_only": sum(1 for r in rows if r["portability_tier"] == "B"),
        "n_core": sum(1 for r in rows if r["selection_tier"] == "CORE"),
        "n_algorithms": len({r["algorithm"] for r in rows}),
        "n_failed_attempts": len(skipped),
    }
    (OUT / "provenance.json").write_text(json.dumps(prov, indent=2))
    print(json.dumps(prov, indent=2))


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run_pending(float(sys.argv[2]))
    else:
        materialise()
