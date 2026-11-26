#!/usr/bin/env python3
"""qcm-pipeline worker: Kirin / Bloqade.

Self-contained by design (no shared modules across toolchains).
Protocol: one JSON job per stdin line -> one JSON result per stdout line.
Events are appended to <out>/events_kirin.csv.

Pipeline (bloqade-circuit, OpenQASM 2 input only):
  qasm2.loads -> .similar(qasm2.extended) -> QASM2Py -> QASM2Fold -> UOpToParallel
QASM2Py converts QASM's expression dialect into Python-dialect
expressions, which the parallelisation analysis requires.

Tracing: every kirin.passes.Pass subclass has its unsafe_run wrapped,
so passes that run without being configured (Fold, HintConst,
TypeInfer, ... called from inside other passes) are all recorded, with
nesting depth and parent. Inside passes, every iteration of a
kirin.rewrite.Fixpoint (a rewrite rule applied until it stops changing
the IR) is one event of pass_kind "rewrite_iteration", named after the
rules it applies, e.g. Fixpoint[ConstantFold+DeadCodeElimination]. The
number of iterations depends on the circuit. Rewrite iterations do not
make their pass a container, and record no memory (resetting the
tracemalloc peak would truncate the enclosing pass's peak).
ir_changed is Kirin's own RewriteResult.has_done_something.
Tracing overhead (IR size walks, bookkeeping) is subtracted from every
enclosing event.

No routing: Kirin/Bloqade has no coupling-map router for this input;
the job's device is ignored and this is recorded, not hidden.
"""
import argparse
import csv
import functools
import json
import os
import sys
import time
import tracemalloc
from importlib.metadata import version

import bloqade.qasm2 as q2
from bloqade.qasm2.passes import QASM2Fold, QASM2Py, UOpToParallel
from kirin.passes import Pass
from kirin.rewrite import Fixpoint

TOOLCHAIN = "kirin"
VERSIONS = {"kirin-toolchain": version("kirin-toolchain"),
            "bloqade-circuit": version("bloqade-circuit")}
CONFIGURED = (QASM2Py, QASM2Fold, UOpToParallel)
FIELDS = ["case_id", "run_token", "toolchain", "phase", "event_index", "seq",
          "activity", "activity_module", "pass_kind", "nesting_depth",
          "parent_activity", "is_container", "iteration", "start_unix_ns",
          "duration_ns", "ir_changed", "changed_method", "size_before",
          "size_after", "mem_peak_bytes"]

_CTX = {"rec": None, "stack": [], "phase": "compile", "overhead": 0}


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


def ir_size(mt):
    try:
        return sum(1 for _ in mt.callable_region.walk())
    except Exception:
        return ""


def _subclasses(cls):
    out = set()
    for s in cls.__subclasses__():
        out |= {s} | _subclasses(s)
    return out


def node_size(node):
    try:
        return sum(1 for _ in node.walk())
    except Exception:
        return ""


def rule_name(rule):
    """Readable name of a rewrite rule tree: Walk/Fixpoint unwrap, Chain joins with '+'."""
    if hasattr(rule, "rules"):
        return "+".join(rule_name(r) for r in rule.rules)
    if hasattr(rule, "rule"):
        return rule_name(rule.rule)
    return type(rule).__name__


def _overhead_since(o0):
    """Charge tracer work done since o0 to every enclosing timed event."""
    _CTX["overhead"] += time.perf_counter_ns() - o0


def install_tracing():
    """Wrap unsafe_run on every Pass subclass (idempotent; re-run per job)."""
    for cls in _subclasses(Pass):
        orig = cls.__dict__.get("unsafe_run")
        if orig is None or getattr(orig, "_qcm_traced", False):
            continue

        def make(cls, orig):
            @functools.wraps(orig)
            def unsafe_run(self, mt):
                rec = _CTX["rec"]
                if rec is None:
                    return orig(self, mt)
                o0 = time.perf_counter_ns()
                stack = _CTX["stack"]
                frame = {"seq": rec.next_seq(), "children": 0,
                         "parent": stack[-1]["name"] if stack else "",
                         "depth": len(stack), "name": cls.__name__,
                         "size": ir_size(mt)}
                if stack:
                    stack[-1]["children"] += 1
                stack.append(frame)
                if tracemalloc.is_tracing():
                    tracemalloc.reset_peak()
                _overhead_since(o0)
                ov0, wall, t0 = _CTX["overhead"], time.time_ns(), time.perf_counter_ns()
                result = None
                try:
                    result = orig(self, mt)
                    return result
                finally:
                    t1 = time.perf_counter_ns()
                    dur = (t1 - t0) - (_CTX["overhead"] - ov0)
                    mem = tracemalloc.get_traced_memory()[1] if tracemalloc.is_tracing() else ""
                    stack.pop()
                    rec.add(seq=frame["seq"], phase=_CTX["phase"], activity=cls.__name__,
                            activity_module=cls.__module__,
                            pass_kind="configured" if cls in CONFIGURED else "internal",
                            nesting_depth=frame["depth"], parent_activity=frame["parent"],
                            is_container=frame["children"] > 0, start_unix_ns=wall,
                            duration_ns=dur,
                            ir_changed=getattr(result, "has_done_something", ""),
                            changed_method="rewrite_result", size_before=frame["size"],
                            size_after=ir_size(mt), mem_peak_bytes=mem)
                    _overhead_since(t1)
            unsafe_run._qcm_traced = True
            return unsafe_run

        cls.unsafe_run = make(cls, orig)


def install_fixpoint_tracing():
    """Record every iteration of Kirin's own Fixpoint loop (idempotent).

    Kirin's loop is left untouched: for the duration of one Fixpoint.rewrite
    call, the inner rule's rewrite method is shadowed on that instance by a
    timing wrapper, so each call the loop makes becomes one event.
    """
    orig = Fixpoint.rewrite
    if getattr(orig, "_qcm_traced", False):
        return

    @functools.wraps(orig)
    def rewrite(self, node):
        rec = _CTX["rec"]
        rule = self.rule
        if rec is None:
            return orig(self, node)
        name, inner = f"Fixpoint[{rule_name(rule)}]", rule.rewrite

        def traced(n):
            o0 = time.perf_counter_ns()
            stack = _CTX["stack"]
            seq, depth = rec.next_seq(), len(stack)
            parent = stack[-1]["name"] if stack else ""
            size0 = node_size(n)
            _overhead_since(o0)
            ov0, wall, t0 = _CTX["overhead"], time.time_ns(), time.perf_counter_ns()
            result = None
            try:
                result = inner(n)
                return result
            finally:
                t1 = time.perf_counter_ns()
                rec.add(seq=seq, phase=_CTX["phase"], activity=name,
                        activity_module=Fixpoint.__module__, pass_kind="rewrite_iteration",
                        nesting_depth=depth, parent_activity=parent, is_container=False,
                        start_unix_ns=wall, duration_ns=(t1 - t0) - (_CTX["overhead"] - ov0),
                        ir_changed=getattr(result, "has_done_something", ""),
                        changed_method="rewrite_result", size_before=size0,
                        size_after=node_size(n), mem_peak_bytes="")
                _overhead_since(t1)

        prev = rule.__dict__.get("rewrite")
        object.__setattr__(rule, "rewrite", traced)
        try:
            return orig(self, node)
        finally:
            if prev is None:
                object.__delattr__(rule, "rewrite")
            else:
                object.__setattr__(rule, "rewrite", prev)

    rewrite._qcm_traced = True
    Fixpoint.rewrite = rewrite


def load(job):
    if job["format"] != "qasm2":
        raise ValueError("bloqade.qasm2 reads OpenQASM 2 only")
    return q2.loads(job["qasm"])


def compile_circuit(mt, job, rec):
    mt = mt.similar(q2.extended)
    for P in CONFIGURED:
        P(mt.dialects)(mt)
    n = ir_size(mt)
    return n, ""


def run_job(job, events_path):
    res = {"case_id": job["case_id"], "run_token": job["run_token"],
           "toolchain": TOOLCHAIN, "status": "ok", "error": "", "load_ms": "",
           "compile_ms": "", "n_events": 0, "out_ops": "", "out_2q_ops": "",
           "versions": VERSIONS, "pid": os.getpid(), "note": "no routing"}
    rec = Recorder(job)
    install_tracing()
    install_fixpoint_tracing()
    _CTX.update(rec=rec, stack=[], overhead=0)
    try:
        try:
            _CTX["phase"] = "load"
            t0 = time.perf_counter()
            mt = load(job)
            res["load_ms"] = round((time.perf_counter() - t0) * 1e3, 3)
        except Exception as e:
            res.update(status="load_error", error=f"{type(e).__name__}: {str(e)[:200]}")
            return res
        try:
            _CTX["phase"] = "compile"
            if job.get("trace_memory"):
                tracemalloc.start()
            t0 = time.perf_counter()
            res["out_ops"], res["out_2q_ops"] = compile_circuit(mt, job, rec)
            res["compile_ms"] = round((time.perf_counter() - t0) * 1e3, 3)
        except Exception as e:
            res.update(status="compile_error", error=f"{type(e).__name__}: {str(e)[:200]}")
        finally:
            if tracemalloc.is_tracing():
                tracemalloc.stop()
    finally:
        _CTX.update(rec=None, stack=[])
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
