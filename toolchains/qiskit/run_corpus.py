#!/usr/bin/env python3
"""qcm-pipeline worker: Qiskit.

Self-contained by design (no shared modules across toolchains).
Protocol: one JSON job per stdin line -> one JSON result per stdout line.
Events are appended to <out>/events_qiskit.csv.

Pipeline: generate_preset_pass_manager at Qiskit's default optimisation
level (2) against a GenericBackendV2 with basis {cz, u} and the job's
coupling map. Every pass is observed through the pass-manager callback;
Qiskit measures pass time itself, so tracing overhead is excluded.
"""
import argparse
import csv
import json
import os
import sys
import time as _time
import tracemalloc
from importlib.metadata import version

from qiskit import qasm2, qasm3
from qiskit.converters import circuit_to_dag
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.transpiler import CouplingMap, generate_preset_pass_manager

TOOLCHAIN = "qiskit"
VERSIONS = {"qiskit": version("qiskit")}
DEFAULT_OPT_LEVEL = 2  # Qiskit's own default for transpile()
BASIS = ["cz", "u"]
FIELDS = ["case_id", "run_token", "toolchain", "phase", "event_index", "seq",
          "activity", "activity_module", "pass_kind", "nesting_depth",
          "parent_activity", "is_container", "iteration", "start_unix_ns",
          "duration_ns", "ir_changed", "changed_method", "size_before",
          "size_after", "mem_peak_bytes"]


# ------------------------------------------------------------ event buffer --
class Recorder:
    def __init__(self, job):
        self.job, self.events, self.seq = job, [], 0

    def add(self, **ev):
        ev["seq"] = self.seq
        self.seq += 1
        self.events.append(ev)

    def flush(self, path):
        self.events.sort(key=lambda e: e["seq"])
        seen = {}
        rows = []
        for i, ev in enumerate(self.events):
            seen[ev["activity"]] = seen.get(ev["activity"], 0) + 1
            row = {k: "" for k in FIELDS}
            row.update(ev)
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


def _param(x):
    try:
        return round(float(x), 10)
    except Exception:
        return hash(x.tobytes()) if hasattr(x, "tobytes") else str(x)


def dag_fingerprint(dag):
    return hash(tuple(
        (n.op.name, tuple(dag.find_bit(q).index for q in n.qargs),
         tuple(_param(p) for p in n.op.params))
        for n in dag.topological_op_nodes()))


def dag_size(dag):
    """Op count; control-flow blocks are counted recursively."""
    try:
        return dag.size(recurse=True)
    except Exception:
        return len(dag.op_nodes())


def mem_mark():
    """Peak Python-heap bytes since the previous mark, then reset."""
    if not tracemalloc.is_tracing():
        return ""
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.reset_peak()
    return peak


# ------------------------------------------------------------------ steps --
def load(job):
    if job["format"] == "qasm2":
        return qasm2.loads(job["qasm"],
                           custom_instructions=qasm2.LEGACY_CUSTOM_INSTRUCTIONS,
                           custom_classical=qasm2.LEGACY_CUSTOM_CLASSICAL)
    return qasm3.loads(job["qasm"])  # needs qiskit-qasm3-import


def stage_index(pm):
    """id(pass instance) -> native stage name ('layout', 'routing', ...)."""
    def walk(task, acc):
        kids = getattr(task, "tasks", None)
        if kids is None:
            acc.append(task)
            return
        for k in kids:
            walk(k, acc)
    idx = {}
    for st in pm.stages:
        for sub in ("pre_" + st, st, "post_" + st):
            spm = getattr(pm, sub, None)
            if spm is None:
                continue
            acc = []
            walk(spm.to_flow_controller(), acc)
            for p in acc:
                idx.setdefault(id(p), sub)
    return idx


def compile_circuit(circ, job, rec):
    dev = job["device"]
    edges = [tuple(e) for e in dev["edges"]]
    cmap = CouplingMap(edges + [(b, a) for a, b in edges]) if edges else None
    backend = GenericBackendV2(num_qubits=dev["num_qubits"], basis_gates=BASIS,
                               coupling_map=cmap, control_flow=True,
                               seed=job["seed"])
    level = job["opt_level"].get(TOOLCHAIN, DEFAULT_OPT_LEVEL)
    pm = generate_preset_pass_manager(optimization_level=level, backend=backend,
                                      seed_transpiler=job["seed"])
    stages = stage_index(pm)
    dag0 = circuit_to_dag(circ)
    state = {"fp": dag_fingerprint(dag0), "size": dag_size(dag0)}
    mem_mark()

    def callback(pass_=None, dag=None, time=None, property_set=None, count=None):
        end_wall = _time.time_ns()
        mem = mem_mark()
        dur = int(time * 1e9)
        fp = dag_fingerprint(dag)
        rec.add(phase="compile", activity=type(pass_).__name__,
                activity_module=type(pass_).__module__,
                pass_kind="analysis" if pass_.is_analysis_pass else "transformation",
                nesting_depth=0,
                parent_activity="stage:" + stages.get(id(pass_), "unknown"),
                is_container=False, start_unix_ns=end_wall - dur, duration_ns=dur,
                ir_changed=fp != state["fp"], changed_method="dag_fingerprint",
                size_before=state["size"], size_after=dag_size(dag),
                mem_peak_bytes=mem)
        state["fp"], state["size"] = fp, dag_size(dag)
        mem_mark()  # exclude fingerprinting from the next pass's peak

    out = pm.run(circ, callback=callback)
    two_q = sum(1 for ins in out.data if len(ins.qubits) == 2)
    return dag_size(circuit_to_dag(out)), two_q


# ------------------------------------------------------------------ server --
def run_job(job, events_path):
    res = {"case_id": job["case_id"], "run_token": job["run_token"],
           "toolchain": TOOLCHAIN, "status": "ok", "error": "", "load_ms": "",
           "compile_ms": "", "n_events": 0, "out_ops": "", "out_2q_ops": "",
           "versions": VERSIONS, "pid": os.getpid()}
    rec = Recorder(job)
    try:
        t0 = _time.perf_counter()
        circ = load(job)
        res["load_ms"] = round((_time.perf_counter() - t0) * 1e3, 3)
    except Exception as e:
        res.update(status="load_error", error=f"{type(e).__name__}: {str(e)[:200]}")
        return res
    try:
        if job.get("trace_memory"):
            tracemalloc.start()
        t0 = _time.perf_counter()
        res["out_ops"], res["out_2q_ops"] = compile_circuit(circ, job, rec)
        res["compile_ms"] = round((_time.perf_counter() - t0) * 1e3, 3)
    except Exception as e:
        res.update(status="compile_error", error=f"{type(e).__name__}: {str(e)[:200]}")
    finally:
        if tracemalloc.is_tracing():
            tracemalloc.stop()
    if not job.get("warmup"):
        res["n_events"] = rec.flush(events_path)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    proto = os.fdopen(os.dup(1), "w", buffering=1)
    os.dup2(2, 1)            # library chatter -> stderr, protocol stays clean
    sys.stdout = sys.stderr
    events_path = os.path.join(args.out, f"events_{TOOLCHAIN}.csv")
    for line in sys.stdin:
        if line.strip():
            proto.write(json.dumps(run_job(json.loads(line), events_path)) + "\n")


if __name__ == "__main__":
    main()
