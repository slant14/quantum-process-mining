"""Recursive pass tracer for BQSKit workflows.

Lives in its own module because BQSKit executes passes in runtime
worker processes: the wrapper class must be importable there, so
run_corpus.py puts this folder on PYTHONPATH before starting Compiler.

Each traced pass appends one JSON line to a per-case sink file.
Tracing overhead (fingerprinting) is subtracted from enclosing passes.
Durations are wall-clock inside BQSKit's cooperative async runtime:
a pass that awaits sub-tasks includes time spent in interleaved tasks.
"""
import json
import os
import time

from bqskit.compiler import BasePass, Workflow

_STATE = {"overhead": 0, "seq": 0}


def _fingerprint(circuit):
    return hash(tuple((op.gate.name, tuple(op.location),
                       tuple(round(float(p), 10) for p in op.params))
                      for op in circuit))


def _children(p):
    if isinstance(p, Workflow):
        return list(p._passes)
    out = []
    for v in vars(p).values():
        if isinstance(v, BasePass):
            out.append(v)
        elif isinstance(v, (list, tuple)) and v and all(isinstance(x, BasePass) for x in v):
            out.extend(v)
    return out


class Traced(BasePass):
    def __init__(self, inner, sink, depth, parent, is_container):
        self.inner, self.sink = inner, sink
        self.depth, self.parent, self.is_container = depth, parent, is_container

    @property
    def name(self):
        return type(self.inner).__name__

    async def run(self, circuit, data):
        o0 = time.perf_counter_ns()
        seq = _STATE["seq"]
        _STATE["seq"] += 1
        fp0, n0 = _fingerprint(circuit), circuit.num_operations
        _STATE["overhead"] += time.perf_counter_ns() - o0
        ov0, wall, t0 = _STATE["overhead"], time.time_ns(), time.perf_counter_ns()
        err = ""
        try:
            await self.inner.run(circuit, data)
        except Exception as e:
            err = type(e).__name__
            raise
        finally:
            t1 = time.perf_counter_ns()
            o1 = time.perf_counter_ns()
            rec = {"seq": seq, "activity": type(self.inner).__name__,
                   "activity_module": type(self.inner).__module__,
                   "nesting_depth": self.depth, "parent_activity": self.parent,
                   "is_container": self.is_container, "start_unix_ns": wall,
                   "duration_ns": (t1 - t0) - (_STATE["overhead"] - ov0),
                   "ir_changed": (_fingerprint(circuit) != fp0) if not err else "",
                   "size_before": n0, "size_after": circuit.num_operations,
                   "pid": os.getpid(), "error": err}
            with open(self.sink, "a") as fh:
                fh.write(json.dumps(rec) + "\n")
            _STATE["overhead"] += time.perf_counter_ns() - o1


def trace(p, sink, depth=0, parent=""):
    """Wrap p and, recursively, every pass nested inside it."""
    me = type(p).__name__
    kids = _children(p)
    if isinstance(p, Workflow):
        p._passes = [trace(q, sink, depth + 1, me) for q in p._passes]
    else:
        for k, v in list(vars(p).items()):
            if isinstance(v, BasePass):
                setattr(p, k, trace(v, sink, depth + 1, me))
            elif isinstance(v, (list, tuple)) and v and all(isinstance(x, BasePass) for x in v):
                setattr(p, k, type(v)(trace(x, sink, depth + 1, me) for x in v))
    return Traced(p, sink, depth, parent, is_container=bool(kids))
