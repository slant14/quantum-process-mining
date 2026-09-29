#!/usr/bin/env python3
"""qcm-pipeline worker: PennyLane.

Self-contained by design (no shared modules across toolchains).
Protocol: one JSON job per stdin line -> one JSON result per stdout line.
Events are appended to <out>/events_pennylane.csv.

QASM import goes through qml.from_qasm, which requires the
pennylane-qiskit plugin (PennyLane has no native QASM 2 parser; its
native from_qasm3 rejects `include`). The plugin pins its own Qiskit,
which is why PennyLane needs its own virtual environment.

Pipeline: decompose -> transpile(coupling_map) -> decompose ->
qml.compile's default pipeline applied transform by transform
(commute_controlled, cancel_inverses, merge_rotations, remove_barrier).
PennyLane's decompose does not reach CZ from CNOT, so the basis is
{CNOT, RX, RY, RZ}; this is documented rather than forced.
"""
import argparse
import csv
import json
import os
import sys
import time
import tracemalloc
from importlib.metadata import version

import pennylane as qml

TOOLCHAIN = "pennylane"
VERSIONS = {"pennylane": version("pennylane"),
            "pennylane-qiskit": version("pennylane-qiskit")}
GATE_SET = {"CNOT", "RX", "RY", "RZ"}
FIELDS = ["case_id", "run_token", "toolchain", "phase", "event_index", "seq",
          "activity", "activity_module", "pass_kind", "nesting_depth",
          "parent_activity", "is_container", "iteration", "start_unix_ns",
          "duration_ns", "ir_changed", "changed_method", "size_before",
          "size_after", "mem_peak_bytes"]


class Recorder:
    def __init__(self, job):
        self.job, self.events, self.seq = job, [], 0

    def add(self, **ev):
        ev["seq"] = self.seq
        self.seq += 1
        self.events.append(ev)

    def flush(self, path):
        self.events.sort(key=lambda e: e["seq"])
        seen, rows = {}, []
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
        return str(x)


def tape_fingerprint(tape):
    return hash(tuple((op.name, tuple(op.wires.tolist()),
                       tuple(_param(p) for p in op.parameters))
                      for op in tape.operations))


def load(job):
    if job["format"] != "qasm2":
        raise ValueError("qml.from_qasm (pennylane-qiskit) reads OpenQASM 2 only here")
    return qml.tape.make_qscript(qml.from_qasm(job["qasm"]))()


def compile_circuit(tape, job, rec):
    edges = [tuple(e) for e in job["device"]["edges"]]
    steps = [("decompose", qml.transforms.decompose, {"gate_set": GATE_SET})]
    if edges:
        steps.append(("transpile", qml.transforms.transpile, {"coupling_map": edges}))
        steps.append(("decompose", qml.transforms.decompose, {"gate_set": GATE_SET}))
    steps += [("commute_controlled", qml.transforms.commute_controlled, {}),
              ("cancel_inverses", qml.transforms.cancel_inverses, {}),
              ("merge_rotations", qml.transforms.merge_rotations, {}),
              ("remove_barrier", qml.transforms.remove_barrier, {})]
    for name, tf, kw in steps:
        fp0, n0 = tape_fingerprint(tape), len(tape.operations)
        if tracemalloc.is_tracing():
            tracemalloc.reset_peak()
        wall, t0 = time.time_ns(), time.perf_counter_ns()
        (tape,), _ = tf(tape, **kw)
        dur = time.perf_counter_ns() - t0
        mem = tracemalloc.get_traced_memory()[1] if tracemalloc.is_tracing() else ""
        rec.add(phase="compile", activity=name, activity_module="pennylane.transforms",
                pass_kind="transform", nesting_depth=0, parent_activity="",
                is_container=False, start_unix_ns=wall, duration_ns=dur,
                ir_changed=tape_fingerprint(tape) != fp0,
                changed_method="tape_fingerprint", size_before=n0,
                size_after=len(tape.operations), mem_peak_bytes=mem)
    ops = tape.operations
    return len(ops), sum(1 for o in ops if len(o.wires) == 2)


def run_job(job, events_path):
    res = {"case_id": job["case_id"], "run_token": job["run_token"],
           "toolchain": TOOLCHAIN, "status": "ok", "error": "", "load_ms": "",
           "compile_ms": "", "n_events": 0, "out_ops": "", "out_2q_ops": "",
           "versions": VERSIONS, "pid": os.getpid()}
    rec = Recorder(job)
    try:
        t0 = time.perf_counter()
        tape = load(job)
        res["load_ms"] = round((time.perf_counter() - t0) * 1e3, 3)
    except Exception as e:
        res.update(status="load_error", error=f"{type(e).__name__}: {str(e)[:200]}")
        return res
    try:
        if job.get("trace_memory"):
            tracemalloc.start()
        t0 = time.perf_counter()
        res["out_ops"], res["out_2q_ops"] = compile_circuit(tape, job, rec)
        res["compile_ms"] = round((time.perf_counter() - t0) * 1e3, 3)
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
    os.dup2(2, 1)
    sys.stdout = sys.stderr
    events_path = os.path.join(args.out, f"events_{TOOLCHAIN}.csv")
    for line in sys.stdin:
        if line.strip():
            proto.write(json.dumps(run_job(json.loads(line), events_path)) + "\n")


if __name__ == "__main__":
    main()
