#!/usr/bin/env python3
"""Merge per-toolchain event files into one process-mining event log.

Outputs (in --out, default <results>/merged):
  event_log.csv          every event + case attributes + ontology stage
  event_log_passes.xes   case = one compilation, activity = raw pass name
                         (mine per toolchain: filter on case attribute 'toolchain')
  event_log_stages.xes   activity = ontology stage, pure control-flow wrappers
                         (stage 'control') removed, consecutive repeats
                         collapsed (cross-toolchain view)

Defaults keep only status == ok cases and drop memory-traced repetitions
(tracemalloc inflates timings). Events are joined to cases on
(case_id, run_token), so events from an interrupted, re-run job are ignored.
"""
import argparse
import glob
import os

import pandas as pd
import pm4py

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", default=os.path.join(HERE, "results"))
    ap.add_argument("--out", default="")
    ap.add_argument("--stage-map", default=os.path.join(HERE, "pass_stage_map.csv"))
    ap.add_argument("--include-failed", action="store_true")
    ap.add_argument("--include-mem-reps", action="store_true")
    ap.add_argument("--no-xes", action="store_true")
    args = ap.parse_args()
    out = args.out or os.path.join(args.results, "merged")
    os.makedirs(out, exist_ok=True)

    cases = pd.read_csv(os.path.join(args.results, "cases.csv"), dtype=str)
    if not args.include_failed:
        cases = cases[cases.status == "ok"]
    if not args.include_mem_reps:
        cases = cases[cases.mem_traced.str.lower() != "true"]

    ev = pd.concat([pd.read_csv(f, dtype=str)
                    for f in sorted(glob.glob(os.path.join(args.results, "events_*.csv")))],
                   ignore_index=True)
    keep = ["case_id", "run_token", "circuit_id", "algorithm", "num_qubits",
            "selection_tier", "portability_tier", "rep", "input_sha16", "topology"]
    df = ev.merge(cases[keep + ["status"]], on=["case_id", "run_token"], how="inner")

    smap = pd.read_csv(args.stage_map, dtype=str)[["toolchain", "activity", "stage"]]
    df = df.merge(smap, on=["toolchain", "activity"], how="left")
    df["stage"] = df["stage"].fillna("UNMAPPED")
    df["event_index"] = df["event_index"].astype(int)
    df["start_unix_ns"] = df["start_unix_ns"].astype("int64")
    df = df.sort_values(["case_id", "event_index"]).reset_index(drop=True)
    df.to_csv(os.path.join(out, "event_log.csv"), index=False)

    unm = df[df.stage == "UNMAPPED"].groupby(["toolchain", "activity"]).size()
    print(f"cases={df.case_id.nunique()} events={len(df)} "
          f"toolchains={sorted(df.toolchain.unique())}")
    if len(unm):
        print(f"UNMAPPED activities ({len(unm)}) - add them to {os.path.basename(args.stage_map)}:")
        for (tc, a), n in unm.items():
            print(f"   {tc:10s} {a}  (x{n})")
    if args.no_xes:
        return

    def to_xes(d, activity_col, path):
        x = d.copy()
        x["case:concept:name"] = x["case_id"]
        x["concept:name"] = x[activity_col]
        x["time:timestamp"] = pd.to_datetime(x["start_unix_ns"], unit="ns", utc=True)
        for c in ["toolchain", "circuit_id", "algorithm", "num_qubits",
                  "portability_tier", "selection_tier", "rep"]:
            x["case:" + c] = x[c]
        x = x.sort_values(["case:concept:name", "event_index"])
        pm4py.write_xes(x, path)
        print(f"wrote {os.path.relpath(path)}  ({x['case:concept:name'].nunique()} cases, {len(x)} events)")

    to_xes(df, "activity", os.path.join(out, "event_log_passes.xes"))

    # Drop only pure control flow. Containers such as Kirin's Fold or Cirq's
    # merge_single_qubit_gates_to_phxz do real work themselves, so they stay.
    leaf = df[df.stage != "control"].copy()
    leaf["_prev"] = leaf.groupby("case_id")["stage"].shift()
    stages = leaf[leaf.stage != leaf._prev].drop(columns="_prev")
    to_xes(stages, "stage", os.path.join(out, "event_log_stages.xes"))


if __name__ == "__main__":
    main()
