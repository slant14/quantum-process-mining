#!/usr/bin/env python3
"""Merge per-toolchain event files into one process-mining event log.

Outputs (in --out, default <results>/merged):
  event_log.csv          every event + case attributes + ontology stage
  event_log_passes.xes   case = one compilation, activity = raw pass name
                         (mine per toolchain: filter on case attribute 'toolchain')
  event_log_stages.xes   activity = ontology stage, pure control-flow wrappers
                         (stage 'control') removed, consecutive repeats
                         collapsed (cross-toolchain view)
  event_log.ocel.sqlite  (--ocel) OCEL 2.0, objects: compilation, circuit,
                         toolchain, configuration, pass, stage

Several runs (e.g. one per compiler setting) can be merged into one log:
  merge_logs.py --results v1=results:qiskit,cirq results/v2/qiskit-L3-* --out DIR
Each case is tagged with its run name, opt_level and seed (from the run's
run_config.json), and its case_id is prefixed with the run name.

Defaults keep only status == ok cases and drop memory-traced repetitions
(tracemalloc inflates timings). Events are joined to cases on
(case_id, run_token), so events from an interrupted, re-run job are ignored.

Most failed compilations have no pass events (load errors, timeouts,
crashes, BQSKit refusing to build a workflow), so --include-failed alone
only adds failures that got as far as running a pass. --outcome-events
appends one terminal event per case named after its status, so every
case is in the log, including those with no pass events.
"""
import argparse
import glob
import json
import os

import pandas as pd
import pm4py

HERE = os.path.dirname(os.path.abspath(__file__))
OUTCOME = {"ok": "compilation ok", "load_error": "load error",
           "compile_error": "compile error", "timeout": "timeout", "crash": "crash"}
# each worker's setting when run_all.py gets no --opt-level for it
DEFAULT_LEVEL = {"qiskit": "2", "bqskit": "1", "cirq": "1"}


def parse_spec(spec):
    """'[NAME=]DIR[:TC,TC]' -> (name or None, dir, [toolchains] or None)."""
    name, _, rest = spec.partition("=") if "=" in spec else (None, "", spec)
    path, _, tcs = rest.partition(":")
    return name, path, [t for t in tcs.split(",") if t] or None


def load_run(spec, prefix):
    """Cases and events of one run folder, tagged with the run's name and settings."""
    name, path, tcs = parse_spec(spec)
    name = name or os.path.basename(os.path.normpath(path))
    cfg_path = os.path.join(path, "run_config.json")
    cfg = json.load(open(cfg_path)) if os.path.exists(cfg_path) else {}
    levels = json.loads(cfg.get("opt_level") or "{}")
    cases = pd.read_csv(os.path.join(path, "cases.csv"), dtype=str)
    files = sorted(glob.glob(os.path.join(path, "events_*.csv")))
    if tcs:
        cases = cases[cases.toolchain.isin(tcs)]
        files = [f for f in files if os.path.basename(f)[len("events_"):-len(".csv")] in tcs]
    ev = (pd.concat([pd.read_csv(f, dtype=str) for f in files], ignore_index=True)
          if files else pd.DataFrame(columns=["case_id", "run_token", "toolchain"]))
    cases = cases.assign(
        run=name, seed=str(cfg.get("seed", "")),
        opt_level=cases.toolchain.map(lambda t: str(levels.get(t, DEFAULT_LEVEL.get(t, "default")))))
    if prefix:
        cases["case_id"] = name + "/" + cases["case_id"]
        ev["case_id"] = name + "/" + ev["case_id"]
    return cases, ev


def outcome_events(cases, df):
    """One terminal event per case: 1 us after its last pass ends (so it still sorts last
    at microsecond resolution), or at finished_utc if no pass ran."""
    end = (df["start_unix_ns"] + pd.to_numeric(df["duration_ns"]).fillna(0).astype("int64"))
    last = (df.assign(_end=end).groupby("case_id")
            .agg(n_pass_events=("event_index", "size"), last_end=("_end", "max"))
            .astype("Int64"))  # nullable: a float64 NaN column would round ns timestamps
    o = cases.join(last, on="case_id")
    finished = ((pd.to_datetime(o["finished_utc"], utc=True) - pd.Timestamp(0, tz="UTC"))
                // pd.Timedelta(1, "ns"))
    o["start_unix_ns"] = (o["last_end"] + 1000).fillna(0).astype("int64").clip(lower=finished)
    o["event_index"] = o["n_pass_events"].fillna(0).astype(int)
    o["activity"] = o["status"].map(OUTCOME).fillna(o["status"])
    return o.drop(columns=["n_pass_events", "last_end", "finished_utc"]).assign(
        phase="outcome", seq=None, activity_module="qcm-pipeline", pass_kind="outcome",
        nesting_depth=0, parent_activity=None, is_container=False, iteration=1,
        duration_ns=None, ir_changed=None, changed_method=None, size_before=None,
        size_after=None, mem_peak_bytes=None)


def to_ocel(df, cases, smap, manifest_path, path):
    """OCEL 2.0 view of the merged log.

    Objects: compilation (one per case), circuit, toolchain, configuration
    (toolchain + opt level + topology + seed), pass (one per toolchain + pass
    class, or + rewrite rule for Kirin's Fixpoint iterations), stage (ontology).
    Every event is related to its compilation, circuit, toolchain and
    configuration; pass events also to their pass and stage.
    Events within a compilation have strictly increasing timestamps, but
    event_index stays the authoritative order.
    """
    from pm4py.objects.ocel.obj import OCEL

    num = lambda s: pd.to_numeric(s, errors="coerce")
    boolean = lambda s: s.astype("string").str.lower().map({"true": True, "false": False})
    df = df.reset_index(drop=True)
    is_pass = df["phase"] != "outcome"
    pass_oid = df["toolchain"] + ":" + df["activity"]
    config_id = lambda d: (d["toolchain"] + "|level=" + d["opt_level"] + "|" + d["topology"]
                           + "|seed=" + d["seed"])
    cinfo = cases.set_index("case_id")

    events = pd.DataFrame({
        "ocel:eid": df["case_id"] + "#" + df["event_index"].astype(str),
        "ocel:activity": df["activity"],
        "ocel:timestamp": pd.to_datetime(df["start_unix_ns"], unit="ns", utc=True),
        "event_index": df["event_index"],
        "pass_kind": df["pass_kind"],
        "nesting_depth": num(df["nesting_depth"]),
        "parent_activity": df["parent_activity"],
        "is_container": boolean(df["is_container"]),
        "iteration": num(df["iteration"]),
        "duration_ns": num(df["duration_ns"]),
        "ir_changed": boolean(df["ir_changed"]),
        "changed_method": df["changed_method"],
        "size_before": num(df["size_before"]),
        "size_after": num(df["size_after"]),
        "mem_peak_bytes": num(df["mem_peak_bytes"]),
    })
    for col in ["error", "load_ms", "compile_ms"]:  # outcome events only
        v = df["case_id"].map(cinfo[col])
        events[col] = (num(v) if col.endswith("_ms") else v).where(~is_pass)

    def links(mask, oids, otype, qualifier):
        return pd.DataFrame({"ocel:eid": events["ocel:eid"][mask],
                             "ocel:activity": events["ocel:activity"][mask],
                             "ocel:timestamp": events["ocel:timestamp"][mask],
                             "ocel:oid": oids[mask], "ocel:type": otype,
                             "ocel:qualifier": qualifier})
    every = pd.Series(True, index=df.index)
    relations = pd.concat([
        links(every, df["case_id"], "compilation", "of compilation"),
        links(every, df["circuit_id"], "circuit", "input circuit"),
        links(every, df["toolchain"], "toolchain", "by toolchain"),
        links(every, config_id(df), "configuration", "under configuration"),
        links(is_pass, pass_oid, "pass", "executes pass"),
        links(is_pass, df["stage"], "stage", "in stage"),
    ], ignore_index=True)

    comp = cases.rename(columns={"case_id": "ocel:oid", "n_events": "n_pass_events"})[
        ["ocel:oid", "run", "opt_level", "seed", "rep", "mem_traced", "status", "error",
         "load_ms", "compile_ms", "n_pass_events", "out_ops", "out_2q_ops", "topology",
         "device_qubits", "barriers_stripped", "input_format", "input_sha16"]].assign(
        **{"ocel:type": "compilation"})
    for col in ["rep", "load_ms", "compile_ms", "n_pass_events", "out_ops", "out_2q_ops",
                "device_qubits"]:
        comp[col] = num(comp[col])
    for col in ["mem_traced", "barriers_stripped"]:
        comp[col] = boolean(comp[col])

    circ_cols = ["algorithm", "description", "stress_class", "selection_tier",
                 "portability_tier", "level", "num_qubits", "num_clbits", "depth",
                 "num_instructions", "two_qubit_gates", "multi_qubit_gates",
                 "has_dynamic_control", "strict_qelib1", "non_qelib1_gates",
                 "has_barrier", "has_custom_gate_defs", "has_classical_conditional"]
    if os.path.exists(manifest_path):
        man = pd.read_csv(manifest_path, dtype=str).set_index("circuit_id")
    else:
        print(f"note: {manifest_path} not found; circuit objects get case attributes only")
        man = cases.drop_duplicates("circuit_id").set_index("circuit_id")
    man = man[[c for c in circ_cols if c in man.columns]]
    circ = man.loc[sorted(cases["circuit_id"].unique())].reset_index().rename(
        columns={"circuit_id": "ocel:oid"}).assign(**{"ocel:type": "circuit"})
    for col in ["num_qubits", "num_clbits", "depth", "num_instructions",
                "two_qubit_gates", "multi_qubit_gates"]:
        if col in circ:
            circ[col] = num(circ[col])

    # crashed and timed-out cases report no versions ("{}"); prefer a row that has them
    tool = (cases.assign(_v=cases["versions"].fillna("{}") != "{}")
            .sort_values("_v", ascending=False, kind="stable")
            .drop_duplicates("toolchain")[["toolchain", "versions"]]
            .rename(columns={"toolchain": "ocel:oid"}).assign(**{"ocel:type": "toolchain"}))

    conf = cases.assign(**{"ocel:oid": config_id(cases)}).drop_duplicates("ocel:oid")[
        ["ocel:oid", "toolchain", "opt_level", "topology", "seed"]].assign(
        **{"ocel:type": "configuration"})

    p = df[is_pass].assign(**{"ocel:oid": pass_oid[is_pass]}).drop_duplicates("ocel:oid")
    p = p.merge(smap[["toolchain", "activity", "basis", "status"]].rename(
        columns={"basis": "stage_basis", "status": "stage_status"}),
        on=["toolchain", "activity"], how="left")
    # a rewrite rule runs inside many passes, so its stage is per event, not per object
    rw = p["pass_kind"] == "rewrite_iteration"
    p.loc[rw, "stage"] = None
    p.loc[rw, "stage_basis"] = "inherited from the enclosing pass (per event)"
    passes = p[["ocel:oid", "toolchain", "activity", "activity_module", "pass_kind",
                "stage", "stage_basis", "stage_status"]].rename(
        columns={"activity": "name", "activity_module": "module"}).assign(**{"ocel:type": "pass"})

    stages = pd.DataFrame({"ocel:oid": sorted(df.loc[is_pass, "stage"].unique()),
                           "ocel:type": "stage"})
    objects = pd.concat([comp, circ, tool, conf, passes, stages], ignore_index=True)

    mapped = passes[passes["stage"].notna()]
    o2o = pd.concat([
        pd.DataFrame({"ocel:oid": cases["case_id"], "ocel:oid_2": cases["circuit_id"],
                      "ocel:qualifier": "compiles"}),
        pd.DataFrame({"ocel:oid": cases["case_id"], "ocel:oid_2": cases["toolchain"],
                      "ocel:qualifier": "compiled by"}),
        pd.DataFrame({"ocel:oid": cases["case_id"], "ocel:oid_2": config_id(cases),
                      "ocel:qualifier": "compiled with"}),
        pd.DataFrame({"ocel:oid": conf["ocel:oid"], "ocel:oid_2": conf["toolchain"],
                      "ocel:qualifier": "configures"}),
        pd.DataFrame({"ocel:oid": passes["ocel:oid"], "ocel:oid_2": passes["toolchain"],
                      "ocel:qualifier": "belongs to"}),
        pd.DataFrame({"ocel:oid": mapped["ocel:oid"], "ocel:oid_2": mapped["stage"],
                      "ocel:qualifier": "mapped to"}),
    ], ignore_index=True)

    ocel = OCEL(events=events, objects=objects, relations=relations, o2o=o2o)
    pm4py.write_ocel2_sqlite(ocel, path)
    print(f"wrote {os.path.relpath(path)}  ({len(events)} events, {len(objects)} objects, "
          f"{len(relations)} e2o, {len(o2o)} o2o)")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", nargs="+", default=[os.path.join(HERE, "results")],
                    metavar="[NAME=]DIR[:TC,...]",
                    help="one or more run folders; NAME labels the run (default: folder "
                         "name), TC,... keeps only those toolchains. With several runs, "
                         "case ids are prefixed with the run name.")
    ap.add_argument("--out", default="")
    ap.add_argument("--stage-map", default=os.path.join(HERE, "pass_stage_map.csv"))
    ap.add_argument("--include-failed", action="store_true")
    ap.add_argument("--include-mem-reps", action="store_true")
    ap.add_argument("--outcome-events", action="store_true",
                    help="append a terminal event per case named after its status")
    ap.add_argument("--no-xes", action="store_true")
    ap.add_argument("--ocel", action="store_true", help="also write event_log.ocel.sqlite")
    ap.add_argument("--corpus", default=os.path.join(HERE, "qcm-corpus-v1"),
                    help="corpus folder; its manifest.csv gives OCEL circuit attributes")
    args = ap.parse_args()
    if len(args.results) > 1 and not args.out:
        ap.error("--out is required when merging several runs")
    out = args.out or os.path.join(parse_spec(args.results[0])[1], "merged")
    os.makedirs(out, exist_ok=True)

    runs = [load_run(spec, prefix=len(args.results) > 1) for spec in args.results]
    cases = pd.concat([c for c, _ in runs], ignore_index=True)
    ev = pd.concat([e for _, e in runs], ignore_index=True)
    if not args.include_failed:
        cases = cases[cases.status == "ok"]
    if not args.include_mem_reps:
        cases = cases[cases.mem_traced.str.lower() != "true"]

    keep = ["case_id", "run_token", "circuit_id", "algorithm", "num_qubits",
            "selection_tier", "portability_tier", "rep", "input_sha16", "topology",
            "run", "opt_level", "seed"]
    df = ev.merge(cases[keep + ["status", "error"]], on=["case_id", "run_token"], how="inner")
    df["event_index"] = df["event_index"].astype(int)
    df["start_unix_ns"] = df["start_unix_ns"].astype("int64")
    if args.outcome_events:
        df = pd.concat([df, outcome_events(
            cases[keep + ["status", "error", "toolchain", "finished_utc"]], df)],
            ignore_index=True)
    elif args.include_failed:
        missing = (~cases.case_id.isin(df.case_id)).sum()
        if missing:
            print(f"note: {missing} cases have no pass events and are not in the log; "
                  f"add --outcome-events to include them")

    smap = pd.read_csv(args.stage_map, dtype=str)
    df = df.merge(smap[["toolchain", "activity", "stage"]], on=["toolchain", "activity"],
                  how="left")
    # rewrite iterations (Kirin's Fixpoint loops) take the stage of the pass they run
    # in; outside any pass (e.g. while loading) they keep their own mapping, if any
    parent = smap[["toolchain", "activity", "stage"]].rename(
        columns={"activity": "parent_activity", "stage": "_parent_stage"})
    df = df.merge(parent, on=["toolchain", "parent_activity"], how="left")
    inherit = (df.pass_kind == "rewrite_iteration") & df["_parent_stage"].notna()
    df["stage"] = df["_parent_stage"].where(inherit, df["stage"])
    df = df.drop(columns="_parent_stage")
    df["stage"] = df["stage"].fillna("UNMAPPED").where(df.phase != "outcome", "outcome")
    df = df.sort_values(["case_id", "event_index"]).reset_index(drop=True)
    df.to_csv(os.path.join(out, "event_log.csv"), index=False)

    unm = (df[(df.stage == "UNMAPPED") & (df.pass_kind != "rewrite_iteration")]
           .groupby(["toolchain", "activity"]).size())
    unm_rw = ((df.stage == "UNMAPPED") & (df.pass_kind == "rewrite_iteration")).sum()
    if unm_rw:
        print(f"note: {unm_rw} rewrite iterations ran outside a mapped pass and are UNMAPPED")
    print(f"cases={df.case_id.nunique()} events={len(df)} "
          f"toolchains={sorted(df.toolchain.unique())}")
    if len(unm):
        print(f"UNMAPPED activities ({len(unm)}) - add them to {os.path.basename(args.stage_map)}:")
        for (tc, a), n in unm.items():
            print(f"   {tc:10s} {a}  (x{n})")
    if args.ocel:
        to_ocel(df, cases, smap, os.path.join(args.corpus, "manifest.csv"),
                os.path.join(out, "event_log.ocel.sqlite"))
    if args.no_xes:
        return

    def to_xes(d, activity_col, path):
        x = d.copy()
        x["case:concept:name"] = x["case_id"]
        x["concept:name"] = x[activity_col]
        x["time:timestamp"] = pd.to_datetime(x["start_unix_ns"], unit="ns", utc=True)
        for c in ["toolchain", "circuit_id", "algorithm", "num_qubits",
                  "portability_tier", "selection_tier", "rep", "status", "error",
                  "run", "opt_level", "topology", "seed"]:
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
