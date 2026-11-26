"""Reproduce the README's headline counts and the memory-repetition check (issue #1).

    python paper1/scripts/headline_counts.py

Prints a Markdown table (ready to paste into the issue) and exits with status 1
if a count differs from the README.

Definitions (they match the README's numbers; see the notes printed below):
- pass events: phase != "outcome"; outcome events: phase == "outcome" (one per case)
- a pass sequence is a case's activities ordered by event_index, outcome event
  left out, counted over status == "ok" compilations; top-level keeps only
  nesting_depth == 0
- variants: distinct pass sequences of Qiskit, opt_level 2, grid, seed 42, rep 0, ok
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd  # noqa: E402
from load_log import load_log  # noqa: E402

EXPECTED = {
    "events": 1_773_352, "pass events": 1_754_405, "outcome events": 18_947,
    "timing compilations": 18_947, "ok": 17_546, "failed": 1_401,
    "distinct pass sequences": 987, "top-level sequences": 57,
    "Qiskit O2 grid s42 rep0 ok variants": 8,
}


def sequences(ev):
    """One pass sequence per case, as plain Python tuples (object dtype).

    pandas 3 stores text in pyarrow, and agg(tuple) would give a pyarrow list column,
    on which nunique() is not implemented.
    """
    s = ev.groupby("case_id", sort=False)["activity"].agg(list)
    return pd.Series([tuple(v) for v in s], index=s.index, dtype=object)


def main():
    log = load_log()
    out = log[log.phase == "outcome"]
    ev = log[log.phase != "outcome"].sort_values(["case_id", "event_index"], kind="stable")
    ok_cases = set(out.case_id[out.status == "ok"])
    ok_ev = ev[ev.case_id.isin(ok_cases)]
    seq = sequences(ok_ev)
    top = sequences(ok_ev[ok_ev.nesting_depth == 0])
    q = ok_ev[(ok_ev.toolchain == "qiskit") & (ok_ev.opt_level == "2")
              & (ok_ev.topology == "grid") & (ok_ev.seed == "42") & (ok_ev.rep == 0)]
    got = {
        "events": len(log), "pass events": len(ev), "outcome events": len(out),
        "timing compilations": out.case_id.nunique(), "ok": len(ok_cases),
        "failed": out.case_id.nunique() - len(ok_cases),
        "distinct pass sequences": seq.nunique(), "top-level sequences": top.nunique(),
        "Qiskit O2 grid s42 rep0 ok variants": sequences(q).nunique(),
    }
    print("| Count | README | Reproduced | |\n|---|---:|---:|---|")
    bad = 0
    for k, want in EXPECTED.items():
        match = got[k] == want
        bad += not match
        print(f"| {k} | {want:,} | {got[k]:,} | {'✓' if match else '✗'} |")

    print("\nNotes")
    per_tc = seq.groupby(ok_ev.drop_duplicates("case_id").set_index("case_id")
                         .toolchain.reindex(seq.index)).nunique()
    print("- distinct pass sequences per toolchain (ok): "
          + ", ".join(f"{t} {n}" for t, n in per_tc.items()))
    print(f"- with failed compilations included: {sequences(ev).nunique():,} sequences "
          "(Kirin compile errors leave partial traces)")
    print(f"- status: " + ", ".join(f"{s} {n:,}" for s, n in out.status.value_counts().items()))

    print("\nMemory repetitions")
    print(f"- `mem_traced` column in the log: {'mem_traced' in log.columns}")
    print(f"- `rep` values of the cases: " + ", ".join(
        f"{r}: {n:,}" for r, n in out.rep.value_counts().sort_index().items()))
    print(f"- pass events with `mem_peak_bytes`: {int(log.mem_peak_bytes.notna().sum()):,}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
