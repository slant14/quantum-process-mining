#!/usr/bin/env python3
"""Run the qcm corpus through all toolchains, one compilation at a time.

Design (see README for rationale):
  * one long-lived worker process per toolchain, each in its own venv;
    workers never import each other or anything shared;
  * jobs = circuit x toolchain x repetition, shuffled with a fixed seed so
    no toolchain always runs first or last (thermal/cache drift);
  * strictly sequential: exactly one compilation runs at any moment;
  * a warm-up compilation is discarded every time a worker (re)starts;
  * a per-compilation timeout kills the worker's whole process group
    (BQSKit spawns runtime children) and restarts it;
  * identical input: the orchestrator reads each QASM file once, applies
    the same preprocessing, and sends the same bytes to every toolchain;
  * resumable: finished case_ids in cases.csv are skipped on restart.
"""
import argparse
import csv
import hashlib
import json
import math
import os
import platform
import queue
import random
import re
import signal
import subprocess
import sys
import threading
import time
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLCHAINS = ["qiskit", "cirq", "pennylane", "bqskit", "kirin"]
CASE_FIELDS = ["case_id", "run_token", "toolchain", "circuit_id", "algorithm",
               "num_qubits", "selection_tier", "portability_tier", "rep",
               "mem_traced", "input_format", "input_sha16", "barriers_stripped",
               "topology", "device_qubits", "status", "error", "load_ms",
               "compile_ms", "n_events", "out_ops", "out_2q_ops", "versions",
               "finished_utc"]


# ------------------------------------------------------------------ device --
def device(n, topology):
    if topology == "all":
        return {"num_qubits": n, "cols": n,
                "edges": [[a, b] for a in range(n) for b in range(a + 1, n)]}
    if topology == "line":
        return {"num_qubits": n, "cols": n, "edges": [[i, i + 1] for i in range(n - 1)]}
    cols = max(1, math.ceil(math.sqrt(n)))
    rows = math.ceil(n / cols)
    edges = []
    for r in range(rows):
        for c in range(cols):
            i = r * cols + c
            if c + 1 < cols:
                edges.append([i, i + 1])
            if r + 1 < rows:
                edges.append([i, i + cols])
    return {"num_qubits": rows * cols, "cols": cols, "edges": edges}


def preprocess(text, strip_barriers):
    return re.sub(r"\bbarrier\b[^;]*;[ \t]*\n?", "", text) if strip_barriers else text


# ------------------------------------------------------------------ worker --
class Worker:
    def __init__(self, tc, python, out_dir, log_dir):
        self.tc, self.python, self.out_dir, self.log_dir = tc, python, out_dir, log_dir
        self.proc, self.q = None, None

    def start(self):
        script = os.path.join(HERE, "toolchains", self.tc, "run_corpus.py")
        self.log = open(os.path.join(self.log_dir, f"worker_{self.tc}.log"), "a")
        self.proc = subprocess.Popen(
            [self.python, script, "--out", self.out_dir],
            cwd=os.path.dirname(script), stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=self.log, text=True, bufsize=1,
            start_new_session=True)
        self.q = queue.Queue()

        def pump(stream, q):
            for line in stream:
                q.put(line)
            q.put(None)
        threading.Thread(target=pump, args=(self.proc.stdout, self.q), daemon=True).start()

    def alive(self):
        return self.proc is not None and self.proc.poll() is None

    def kill(self):
        """Kill the worker and its whole process group; safe if already dead.

        macOS reports EPERM (not ESRCH) when signalling a process group whose
        leader has exited but not been reaped, so both errors mean "gone".
        """
        if self.proc is None:
            return
        pgid = self.proc.pid
        for attempt in (lambda: os.killpg(pgid, signal.SIGKILL), self.proc.kill):
            try:
                attempt()
            except (ProcessLookupError, PermissionError, OSError):
                pass
        self.proc.wait()
        try:  # leader reaped; clear any surviving group members (BQSKit runtime)
            os.killpg(pgid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError, OSError):
            pass
        self.log.close()
        self.proc = None

    def exit_reason(self):
        try:
            rc = self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            return "worker stopped responding"
        if rc is not None and rc < 0:
            try:
                name = signal.Signals(-rc).name
            except ValueError:
                name = f"signal {-rc}"
            hint = {"SIGKILL": " (often the OS killing it for memory)",
                    "SIGSEGV": " (segfault in native code)"}.get(name, "")
            return f"worker killed by {name}{hint}"
        return f"worker exited with code {rc}"

    def send(self, job, timeout):
        """Send one job; return its result, None on timeout. Stale replies are dropped."""
        try:
            self.proc.stdin.write(json.dumps(job) + "\n")
            self.proc.stdin.flush()
        except (BrokenPipeError, OSError):
            return {"status": "crash",
                    "error": f"{self.exit_reason()}; see logs/worker_{self.tc}.log"}
        deadline = time.monotonic() + timeout
        while True:
            try:
                line = self.q.get(timeout=max(0.0, deadline - time.monotonic()))
            except queue.Empty:
                return None
            if line is None:
                return {"status": "crash",
                        "error": f"{self.exit_reason()}; see logs/worker_{self.tc}.log"}
            res = json.loads(line)
            if res.get("case_id") == job["case_id"]:
                return res


# ------------------------------------------------------------------- main --
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus", default=os.path.join(HERE, "..", "qcm-corpus-v1"))
    ap.add_argument("--out", default=os.path.join(HERE, "results"))
    ap.add_argument("--toolchains", default=",".join(TOOLCHAINS))
    ap.add_argument("--selection", default="CORE", choices=["CORE", "ALL"])
    ap.add_argument("--tiers", default="A,A-EXT,B", help="portability tiers to include")
    ap.add_argument("--max-qubits", type=int, default=32)
    ap.add_argument("--algorithms", default="", help="comma list; empty = all")
    ap.add_argument("--limit", type=int, default=0, help="max circuits (smoke tests)")
    ap.add_argument("--reps", type=int, default=3, help="timing repetitions")
    ap.add_argument("--mem-reps", type=int, default=1,
                    help="extra repetitions with tracemalloc on (never mixed with timing)")
    ap.add_argument("--topology", default="grid", choices=["grid", "line", "all"])
    ap.add_argument("--keep-barriers", action="store_true",
                    help="default strips barriers for everyone (Cirq cannot parse them)")
    ap.add_argument("--timeout", type=float, default=600, help="seconds per compilation")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--opt-level", default="",
                    help='JSON overrides, e.g. {"qiskit":3}; default = each toolchain\'s own default')
    ap.add_argument("--python", default="",
                    help='JSON {toolchain: interpreter}; default toolchains/<tc>/.venv/bin/python')
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    corpus = os.path.abspath(args.corpus)
    out = os.path.abspath(args.out)
    os.makedirs(os.path.join(out, "logs"), exist_ok=True)
    tcs = [t for t in args.toolchains.split(",") if t]
    tiers = set(args.tiers.split(","))
    algos = set(a for a in args.algorithms.split(",") if a)
    pythons = json.loads(args.python) if args.python else {}
    opt_level = json.loads(args.opt_level) if args.opt_level else {}

    # ---- select circuits
    rows = list(csv.DictReader(open(os.path.join(corpus, "manifest.csv"))))
    sel = [r for r in rows
           if r["portability_tier"] in tiers
           and (args.selection == "ALL" or r["selection_tier"] == "CORE")
           and int(r["num_qubits"]) <= args.max_qubits
           and (not algos or r["algorithm"] in algos)]
    fileless = [r for r in sel if not r["qasm2_path"] and not r["qasm3_path"]]
    if fileless:  # manifest row with no artifact on disk (corpus < v1.1)
        print(f"skipping {len(fileless)} manifest rows with no QASM file: "
              f"{', '.join(sorted({r['algorithm'] for r in fileless}))}")
        sel = [r for r in sel if r["qasm2_path"] or r["qasm3_path"]]
    sel.sort(key=lambda r: (r["algorithm"], int(r["num_qubits"])))
    if args.limit:
        sel = sel[:args.limit]

    # ---- plan
    n_rep = args.reps + args.mem_reps
    jobs = [(tc, r, rep) for r in sel for tc in tcs for rep in range(n_rep)]
    random.Random(args.seed).shuffle(jobs)
    cases_path = os.path.join(out, "cases.csv")
    done = set()
    if os.path.exists(cases_path):
        done = {r["case_id"] for r in csv.DictReader(open(cases_path))}
    todo = [j for j in jobs if f"{j[0]}__{j[1]['circuit_id']}__r{j[2]}" not in done]
    print(f"circuits={len(sel)} toolchains={tcs} reps={args.reps}+{args.mem_reps}mem "
          f"-> jobs={len(jobs)} already_done={len(jobs) - len(todo)} todo={len(todo)}")
    if args.dry_run or not todo:
        return

    with open(os.path.join(out, "run_config.json"), "w") as fh:
        json.dump({**vars(args), "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "host": platform.platform(), "python": sys.version.split()[0],
                   "corpus_provenance": json.load(open(os.path.join(corpus, "provenance.json")))},
                  fh, indent=2)

    workers = {}
    for tc in tcs:
        py = pythons.get(tc) or os.path.join(HERE, "toolchains", tc, ".venv", "bin", "python")
        if not os.path.exists(py):
            sys.exit(f"missing interpreter for {tc}: {py}  (run setup_envs.sh or pass --python)")
        workers[tc] = Worker(tc, py, out, os.path.join(out, "logs"))

    warm = next((r for r in rows if r["portability_tier"] == "A"
                 and r["algorithm"] == "ghz" and int(r["num_qubits"]) == 4), None)

    def make_job(tc, r, rep, warmup=False):
        fmt = "qasm2" if r["qasm2_path"] else "qasm3"
        raw = open(os.path.join(corpus, r[f"{fmt}_path"])).read()
        text = preprocess(raw, not args.keep_barriers)
        return {"case_id": f"{tc}__{r['circuit_id']}__r{rep}", "run_token": uuid.uuid4().hex,
                "circuit_id": r["circuit_id"], "format": fmt, "qasm": text,
                "input_sha16": hashlib.sha256(text.encode()).hexdigest()[:16],
                "device": device(int(r["num_qubits"]), args.topology), "seed": args.seed,
                "opt_level": opt_level, "trace_memory": rep >= args.reps,
                "warmup": warmup}

    def ensure(tc):
        w = workers[tc]
        if not w.alive():
            w.start()
            if warm is not None:  # discard first compilation after (re)start
                wres = w.send(make_job(tc, warm, -1, warmup=True), max(args.timeout, 300))
                if wres is None or wres.get("status") == "crash":
                    why = "timed out" if wres is None else wres["error"]
                    print(f"warning: {tc} warm-up failed ({why}); continuing without warm-up")
                    w.kill()
                    w.start()

    new_file = not os.path.exists(cases_path)
    fh = open(cases_path, "a", newline="")
    writer = csv.DictWriter(fh, fieldnames=CASE_FIELDS, lineterminator="\n")
    if new_file:
        writer.writeheader()

    t_start = time.time()
    try:
        for k, (tc, r, rep) in enumerate(todo, 1):
            ensure(tc)
            job = make_job(tc, r, rep)
            res = workers[tc].send(job, args.timeout)
            if res is None:
                workers[tc].kill()
                res = {"status": "timeout", "error": f">{args.timeout:.0f}s"}
            elif res.get("status") == "crash":
                workers[tc].kill()
            row = {k2: res.get(k2, "") for k2 in CASE_FIELDS}
            row.update(case_id=job["case_id"], run_token=job["run_token"], toolchain=tc,
                       circuit_id=r["circuit_id"], algorithm=r["algorithm"],
                       num_qubits=r["num_qubits"], selection_tier=r["selection_tier"],
                       portability_tier=r["portability_tier"], rep=rep,
                       mem_traced=job["trace_memory"], input_format=job["format"],
                       input_sha16=job["input_sha16"],
                       barriers_stripped=not args.keep_barriers, topology=args.topology,
                       device_qubits=job["device"]["num_qubits"],
                       versions=json.dumps(res.get("versions", {})),
                       finished_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
            writer.writerow(row)
            fh.flush()
            el = time.time() - t_start
            eta = el / k * (len(todo) - k)
            print(f"[{k}/{len(todo)}] {job['case_id']:<52} {row['status']:<13} "
                  f"{row['compile_ms'] or '-':>10} ms  eta {eta/60:6.1f} min", flush=True)
            if row["status"] == "crash":
                print(f"          -> {row['error']}", flush=True)
    except KeyboardInterrupt:
        print("\ninterrupted - progress saved; re-run the same command to resume")
    finally:
        fh.close()
        for w in workers.values():
            w.kill()


if __name__ == "__main__":
    main()
