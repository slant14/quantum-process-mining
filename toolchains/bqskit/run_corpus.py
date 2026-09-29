#!/usr/bin/env python3
"""qcm-pipeline worker: BQSKit.

Self-contained by design (no shared modules across toolchains);
bqskit_trace.py is this toolchain's own helper, not shared.
Protocol: one JSON job per stdin line -> one JSON result per stdout line.
Events are appended to <out>/events_bqskit.csv.

Pipeline: bqskit.compiler.compile.build_workflow at BQSKit's default
optimisation level (1) for a MachineModel with gate set {CZ, U3} and the
job's coupling graph. Every pass at every nesting level is traced
(IfThenElsePass branches, ForEachBlockPass sub-workflows, synthesis).

Known gotcha: the compiler server drops connections under sustained
sequential use, so a fresh `with Compiler() as comp:` is opened per circuit.
num_workers=1 keeps BQSKit single-worker like the other toolchains.
Per-pass memory is not recorded: passes run in runtime worker processes.
"""
import argparse
import csv
import json
import os
import sys
import tempfile
import time
from importlib.metadata import version

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["PYTHONPATH"] = HERE + os.pathsep + os.environ.get("PYTHONPATH", "")
sys.path.insert(0, HERE)

from bqskit import Circuit, MachineModel  # noqa: E402
from bqskit.compiler import Compiler, Workflow  # noqa: E402
from bqskit.compiler.compile import build_workflow  # noqa: E402
from bqskit.ir.gates import CZGate, U3Gate  # noqa: E402
from bqskit.qis import CouplingGraph  # noqa: E402

from bqskit_trace import trace  # noqa: E402

TOOLCHAIN = "bqskit"
VERSIONS = {"bqskit": version("bqskit")}
DEFAULT_OPT_LEVEL = 1  # BQSKit's own default for compile()
NUM_WORKERS = 1
FIELDS = ["case_id", "run_token", "toolchain", "phase", "event_index", "seq",
          "activity", "activity_module", "pass_kind", "nesting_depth",
          "parent_activity", "is_container", "iteration", "start_unix_ns",
          "duration_ns", "ir_changed", "changed_method", "size_before",
          "size_after", "mem_peak_bytes"]


class Recorder:
    def __init__(self, job):
        self.job, self.events = job, []

    def add(self, **ev):
        self.events.append(ev)

    def flush(self, path):
        self.events.sort(key=lambda e: e["seq"])
        seen, rows = {}, []
        for i, ev in enumerate(self.events):
            seen[ev["activity"]] = seen.get(ev["activity"], 0) + 1
            row = {k: "" for k in FIELDS}
            row.update({k: v for k, v in ev.items() if k in FIELDS})
            row.update(case_id=self.job["case_id"], run_token=self.job["run_token"],
                       toolchain=TOOLCHAIN, event_index=i,
                       iteration=seen[ev["activity"]])
            rows.append(row)
        new = not os.path.exists(path)
        with open(path, "a", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
            if new:
                w.writeheader()
            w.writerows(rows)
        return len(rows)


def load(job, tmpdir):
    if job["format"] != "qasm2":
        raise ValueError("BQSKit's importer reads OpenQASM 2 only")
    path = os.path.join(tmpdir, "in.qasm")
    with open(path, "w") as fh:
        fh.write(job["qasm"])
    return Circuit.from_file(path)


def compile_circuit(circ, job, rec, tmpdir):
    dev = job["device"]
    edges = [tuple(e) for e in dev["edges"]]
    graph = CouplingGraph(edges) if edges else CouplingGraph.all_to_all(dev["num_qubits"])
    model = MachineModel(dev["num_qubits"], graph, gate_set={CZGate(), U3Gate()})
    level = job["opt_level"].get(TOOLCHAIN, DEFAULT_OPT_LEVEL)
    sink = os.path.join(tmpdir, "events.jsonl")
    open(sink, "w").close()
    wf = build_workflow(circ, model, optimization_level=level, seed=job["seed"])
    wf = Workflow([trace(p, sink) for p in wf])
    with Compiler(num_workers=NUM_WORKERS) as comp:
        out = comp.compile(circ, wf)
    with open(sink) as fh:
        for line in fh:
            ev = json.loads(line)
            rec.add(phase="compile", pass_kind="container" if ev["is_container"] else "pass",
                    changed_method="circuit_fingerprint", mem_peak_bytes="", **ev)
    two_q = sum(n for g, n in out.gate_counts.items() if g.num_qudits == 2)
    return out.num_operations, two_q


def run_job(job, events_path):
    res = {"case_id": job["case_id"], "run_token": job["run_token"],
           "toolchain": TOOLCHAIN, "status": "ok", "error": "", "load_ms": "",
           "compile_ms": "", "n_events": 0, "out_ops": "", "out_2q_ops": "",
           "versions": VERSIONS, "pid": os.getpid()}
    rec = Recorder(job)
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            t0 = time.perf_counter()
            circ = load(job, tmpdir)
            res["load_ms"] = round((time.perf_counter() - t0) * 1e3, 3)
        except Exception as e:
            res.update(status="load_error", error=f"{type(e).__name__}: {str(e)[:200]}")
            return res
        try:
            t0 = time.perf_counter()
            res["out_ops"], res["out_2q_ops"] = compile_circuit(circ, job, rec, tmpdir)
            res["compile_ms"] = round((time.perf_counter() - t0) * 1e3, 3)
        except Exception as e:
            res.update(status="compile_error", error=f"{type(e).__name__}: {str(e)[:200]}")
    if not job.get("warmup"):
        res["n_events"] = rec.flush(events_path)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    proto = os.fdopen(os.dup(1), "w", buffering=1)
    os.dup2(2, 1)
    sys.stdout = sys.stderr
    events_path = os.path.join(args.out, f"events_{TOOLCHAIN}.csv")
    for line in sys.stdin:
        if line.strip():
            proto.write(json.dumps(run_job(json.loads(line), events_path)) + "\n")


if __name__ == "__main__":
    main()
