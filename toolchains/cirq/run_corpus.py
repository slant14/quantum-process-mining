#!/usr/bin/env python3
"""qcm-pipeline worker: Cirq.

Self-contained by design (no shared modules across toolchains).
Protocol: one JSON job per stdin line -> one JSON result per stdout line.
Events are appended to <out>/events_cirq.csv.

Cirq has no pass manager, so the pipeline is Cirq's documented
"compile for a device" sequence:
  optimize_for_target_gateset(CZTargetGateset) -> RouteCQC ->
  optimize_for_target_gateset -> merge_single_qubit_gates_to_phxz ->
  eject_phased_paulis -> eject_z -> drop_negligible_operations ->
  drop_empty_moments
Every @cirq.transformer call, including the ones nested inside
optimize_for_target_gateset, is captured through a TransformerLogger.
RouteCQC is not a logged transformer, so it is timed explicitly.
Tracing overhead is subtracted from enclosing transformers.
"""
import argparse
import csv
import json
import os
import sys
import time
import tracemalloc
from importlib.metadata import version

import cirq
import networkx as nx
from cirq.contrib.qasm_import import circuit_from_qasm

TOOLCHAIN = "cirq"
VERSIONS = {"cirq-core": version("cirq-core"), "ply": version("ply")}
FIELDS = ["case_id", "run_token", "toolchain", "phase", "event_index", "seq",
          "activity", "activity_module", "pass_kind", "nesting_depth",
          "parent_activity", "is_container", "iteration", "start_unix_ns",
          "duration_ns", "ir_changed", "changed_method", "size_before",
          "size_after", "mem_peak_bytes"]


class Recorder:
    def __init__(self, job):
        self.job, self.events, self.seq = job, [], 0

    def next_seq(self):
        self.seq += 1
        return self.seq - 1

    def add(self, **ev):
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


def mem_reset():
    if tracemalloc.is_tracing():
        tracemalloc.reset_peak()


def mem_peak():
    return tracemalloc.get_traced_memory()[1] if tracemalloc.is_tracing() else ""


def n_ops(c):
    return sum(1 for _ in c.all_operations())


class TracingLogger(cirq.TransformerLogger):
    """Records every transformer call. Circuits are not retained (memory)."""

    def __init__(self, rec):
        super().__init__()
        self.rec, self.stack, self.overhead = rec, [], 0

    def register_initial(self, circuit, transformer_name):
        o0 = time.perf_counter_ns()
        frame = {"name": transformer_name, "seq": self.rec.next_seq(),
                 "depth": len(self.stack),
                 "parent": self.stack[-1]["name"] if self.stack else "",
                 "before": circuit, "size": n_ops(circuit), "children": 0}
        if self.stack:
            self.stack[-1]["children"] += 1
        self.stack.append(frame)
        mem_reset()
        self.overhead += time.perf_counter_ns() - o0
        frame["ov"], frame["wall"], frame["t0"] = self.overhead, time.time_ns(), time.perf_counter_ns()

    def register_final(self, circuit, transformer_name):
        t1 = time.perf_counter_ns()
        mem = mem_peak()
        f = self.stack.pop()
        dur = (t1 - f["t0"]) - (self.overhead - f["ov"])
        self.rec.add(seq=f["seq"], phase="compile", activity=transformer_name,
                     activity_module="cirq", pass_kind="transformer",
                     nesting_depth=f["depth"], parent_activity=f["parent"],
                     is_container=f["children"] > 0, start_unix_ns=f["wall"],
                     duration_ns=dur, ir_changed=circuit != f["before"],
                     changed_method="circuit_equality", size_before=f["size"],
                     size_after=n_ops(circuit), mem_peak_bytes=mem)
        self.overhead += time.perf_counter_ns() - t1

    def log(self, *args, **kwargs):  # transformers may log debug info; ignore
        pass


def load(job):
    if job["format"] != "qasm2":
        raise ValueError("Cirq's importer reads OpenQASM 2 only")
    return circuit_from_qasm(job["qasm"])


def compile_circuit(circ, job, rec):
    dev = job["device"]
    cols = dev["cols"]
    q = lambda i: cirq.GridQubit(i // cols, i % cols)
    graph = nx.Graph([(q(a), q(b)) for a, b in dev["edges"]])
    graph.add_nodes_from(q(i) for i in range(dev["num_qubits"]))
    lg = TracingLogger(rec)
    ctx = cirq.TransformerContext(logger=lg)
    gs = cirq.CZTargetGateset()

    c = cirq.optimize_for_target_gateset(circ, gateset=gs, context=ctx)

    # RouteCQC: not a @transformer, time it explicitly
    seq, before, size = rec.next_seq(), c, n_ops(c)
    mem_reset()
    wall, t0 = time.time_ns(), time.perf_counter_ns()
    c, _, _ = cirq.RouteCQC(graph).route_circuit(c, context=ctx)
    dur = time.perf_counter_ns() - t0
    rec.add(seq=seq, phase="compile", activity="RouteCQC.route_circuit",
            activity_module="cirq", pass_kind="router", nesting_depth=0,
            parent_activity="", is_container=False, start_unix_ns=wall,
            duration_ns=dur, ir_changed=c != before,
            changed_method="circuit_equality", size_before=size,
            size_after=n_ops(c), mem_peak_bytes=mem_peak())

    c = cirq.optimize_for_target_gateset(c, gateset=gs, context=ctx)
    for tf in (cirq.merge_single_qubit_gates_to_phxz, cirq.eject_phased_paulis,
               cirq.eject_z, cirq.drop_negligible_operations,
               cirq.drop_empty_moments):
        c = tf(c, context=ctx)
    ops = list(c.all_operations())
    return len(ops), sum(1 for o in ops if len(o.qubits) == 2)


def run_job(job, events_path):
    res = {"case_id": job["case_id"], "run_token": job["run_token"],
           "toolchain": TOOLCHAIN, "status": "ok", "error": "", "load_ms": "",
           "compile_ms": "", "n_events": 0, "out_ops": "", "out_2q_ops": "",
           "versions": VERSIONS, "pid": os.getpid()}
    rec = Recorder(job)
    try:
        t0 = time.perf_counter()
        circ = load(job)
        res["load_ms"] = round((time.perf_counter() - t0) * 1e3, 3)
    except Exception as e:
        res.update(status="load_error", error=f"{type(e).__name__}: {str(e)[:200]}")
        return res
    try:
        if job.get("trace_memory"):
            tracemalloc.start()
        t0 = time.perf_counter()
        res["out_ops"], res["out_2q_ops"] = compile_circuit(circ, job, rec)
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
