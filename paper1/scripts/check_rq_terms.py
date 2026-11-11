#!/usr/bin/env python3
"""Check what paper1/docs/research_questions.md says about the data (issue #2).

    python paper1/scripts/check_rq_terms.py           # merged log, manifest, families
    python paper1/scripts/check_rq_terms.py --runs    # also the 52 run folders

Every statement that research_questions.md makes about the merged log, the corpus
manifest, circuit_families.csv or the run folders is one check below. The script
prints each check and the tables the document quotes, and exits with status 1 if any
check fails. When the document changes, change the expected values here with it.

Inputs (defaults relative to the repository root):
  results/merged_v2/event_log.csv   merged v2 log (Zenodo record 23614607)
  qcm-corpus-v1/manifest.csv        corpus manifest
  paper1/docs/circuit_families.csv  algorithm -> family
  pass_stage_map.csv                stage ontology
  results/ and results/v2/*/        run folders, only with --runs. Their CSVs are Git LFS
                                    objects: run `git lfs pull` if they are pointer files.
Needs pandas and numpy only.
"""
import argparse
import glob
import json
import math
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOLCHAINS = ["qiskit", "cirq", "pennylane", "bqskit", "kirin"]
# each toolchain's default (opt_level, topology, seed), as the merged log records it
DEFAULT = {"qiskit": ("2", "grid", "42"), "cirq": ("1", "grid", "42"),
           "bqskit": ("1", "grid", "42"), "pennylane": ("default", "grid", "42"),
           "kirin": ("default", "grid", "42")}
CELL = ["toolchain", "opt_level", "topology", "seed"]
SIZE_BINS, SIZE_LABELS = [1, 5, 12, 20, 32], ["2-5", "6-12", "13-20", "21-32"]
STAGES = ["analysis", "cleanup", "control", "ir_lowering", "layout", "optimization",
          "partitioning", "routing", "scheduling", "setup", "synthesis"]
# columns the document marks E (in event_log.csv) and C (only in the run folders' cases.csv)
E_COLS = ["case_id", "toolchain", "phase", "event_index", "activity", "activity_module",
          "pass_kind", "nesting_depth", "parent_activity", "is_container", "iteration",
          "duration_ns", "ir_changed", "changed_method", "size_before", "size_after",
          "mem_peak_bytes", "stage", "circuit_id", "algorithm", "num_qubits",
          "selection_tier", "rep", "topology", "run", "opt_level", "seed", "status"]
C_COLS = ["device_qubits", "mem_traced", "compile_ms", "load_ms", "n_events", "out_ops",
          "out_2q_ops", "versions", "finished_utc", "input_format", "barriers_stripped"]

FAILED = []


def check(ok, claim):
    print(("  ok    " if ok else "  FAIL  ") + claim)
    if not ok:
        FAILED.append(claim)


def device_qubits(n, topology):
    """Width of the device that run_all.device() builds for an n-qubit circuit."""
    if topology in ("line", "all"):
        return n
    cols = max(1, math.ceil(math.sqrt(n)))
    return math.ceil(n / cols) * cols


def read_csv(path, **kw):
    with open(path, encoding="utf-8", errors="replace") as fh:
        if fh.read(40).startswith("version https://git-lfs"):
            sys.exit(f"{path} is a Git LFS pointer file; run `git lfs pull` first")
    return pd.read_csv(path, keep_default_na=False, **kw)


def check_families(man, fam):
    print("\ncircuit_families.csv and the manifest (D3, D4, section 3.3)")
    check(list(fam.columns) == ["algorithm", "family"], "columns are algorithm, family")
    check(fam.algorithm.is_unique and bool((fam != "").all().all()),
          "one non-empty family per algorithm")
    check(man.algorithm.nunique() == 35 and set(fam.algorithm) == set(man.algorithm),
          "covers exactly the 35 algorithms of the manifest")
    n = fam.family.nunique()
    check(6 <= n <= 8, f"{n} families (6 to 8 wanted)")
    per_alg = man.groupby("algorithm")[["stress_class", "has_dynamic_control",
                                        "selection_tier"]].nunique()
    check(bool((per_alg == 1).all().all()),
          "stress_class, has_dynamic_control and selection_tier are constant per algorithm")
    alg = man.drop_duplicates("algorithm").set_index("algorithm")
    alg["family"] = fam.set_index("algorithm").family
    check(man.stress_class.nunique() == 13, "the manifest has 13 stress classes")
    check(bool((alg.groupby("stress_class").family.nunique() == 1).all()),
          "no stress class is split across families")
    check(bool(((alg.family == "dynamic") == (alg.has_dynamic_control == "True")).all()),
          "family dynamic = the algorithms with has_dynamic_control == True")
    gates = man.ops_histogram.map(lambda h: set(json.loads(h)))
    dyn = man.algorithm.map(alg.family) == "dynamic"
    check(bool((gates.map(lambda g: "if_else" in g) == dyn).all())
          and bool(gates[dyn].map(lambda g: "measure" in g).all()),
          "every dynamic circuit has measure and if_else, and no other circuit has if_else")
    quark = man.algorithm.str.startswith("bmw_quark")
    no_rxx = sorted(man.circuit_id[quark & ~gates.map(lambda g: "rxx" in g)])
    copula = man.algorithm == "bmw_quark_copula"
    check(bool(gates[quark].map(lambda g: {"rx", "rz"} <= g).all())
          and no_rxx == ["bmw_quark_copula_indep_n002"]
          and bool(gates[copula].map(lambda g: {"h", "cx"} <= g).all()),
          "QUARK circuits: rx and rz layers with rxx (copula circuits also h and cx; the "
          "2-qubit copula circuit has no rxx)")

    m = man[man.num_qubits.astype(int) <= 32].assign(family=lambda d: d.algorithm.map(alg.family))
    table = pd.DataFrame({
        "stress_class": alg.groupby("family").stress_class.agg(lambda s: ", ".join(sorted(set(s)))),
        "algorithms": alg.groupby("family").size(),
        "circuits": m.groupby("family").size(),
        "core": m[m.selection_tier == "CORE"].groupby("family").size()})
    table["core"] = table.core.fillna(0).astype(int)
    print(table.to_string())
    got = {f: (int(r.algorithms), int(r.circuits), int(r.core)) for f, r in table.iterrows()}
    check(got == {"arithmetic": (9, 56, 10), "dynamic": (5, 32, 0), "oracle": (4, 40, 26),
                  "qft_qpe": (6, 64, 29), "random": (1, 14, 14), "state_prep": (3, 41, 41),
                  "variational": (7, 90, 56)},
          "family table of D3 (algorithms, compiled circuits, CORE circuits)")

    width = man.num_qubits.astype(int).groupby(man.algorithm)
    lo, hi = width.min(), width.max()
    upto = {"grover": 10, "qwalk": 6, "hhl": 10, "half_adder": 7, "multiplier": 12,
            "rg_qft_multiplier": 12, "bmw_quark_copula": 12}
    only = {"iqpe": 2, "hrs_cumulative_multiplier": 5, "shor": 18}
    check(all(hi[a] == w for a, w in upto.items())
          and all(lo[a] == hi[a] == w for a, w in only.items()),
          "the width limits quoted in D4")
    check(man.level.value_counts().to_dict() == {"indep": 337, "alg": 1}
          and man.circuit_id[man.level == "alg"].tolist() == ["shor_alg_n018"]
          and man.opt_level[man.level == "alg"].tolist() == ["n/a"]
          and set(man.opt_level[man.level == "indep"]) == {"0"},
          "manifest: level indep at opt level 0, except shor_alg_n018 (level alg)")
    check(set(man.seed) == {"", "42"} and int((man.seed == "42").sum()) == 28
          and bool(((man.seed == "42") == (man.seeded == "True")).all()),
          "manifest: seed 42 for the 28 seeded circuits, blank otherwise")
    return alg.family


def check_log(path, man, family, stage_map):
    print(f"\n{os.path.relpath(path, ROOT)}")
    header = list(pd.read_csv(path, nrows=0).columns)
    check(len(header) == 34, f"{len(header)} columns (34 expected)")
    missing = [c for c in E_COLS if c not in header]
    check(not missing, "has every column the document marks E"
          + (f"; missing: {missing}" if missing else ""))
    present = [c for c in C_COLS if c in header]
    check(not present, "has none of the columns the document marks C"
          + (f"; found: {present}" if present else ""))

    cat = ["toolchain", "phase", "activity", "pass_kind", "nesting_depth", "parent_activity",
           "ir_changed", "stage", "circuit_id", "algorithm", "num_qubits", "selection_tier",
           "portability_tier", "rep", "topology", "run", "opt_level", "seed", "status"]
    text = ["case_id", "run_token", "iteration", "mem_peak_bytes"]
    log = read_csv(path, usecols=cat + text,
                   dtype={**{c: "category" for c in cat}, **{c: str for c in text}})
    out, ev = log[log.phase == "outcome"], log[log.phase != "outcome"]
    check(out.case_id.is_unique and len(out) == log.case_id.nunique() == 18947,
          "18,947 cases, each with exactly one outcome event")
    check(len(ev) == 1754405, f"{len(ev):,} pass events (1,754,405 expected)")

    cols = ["case_id", "run_token", "toolchain", "circuit_id", "algorithm", "num_qubits",
            "selection_tier", "portability_tier", "rep", "topology", "run", "opt_level",
            "seed", "status"]
    cases = out[cols].astype(str).reset_index(drop=True)
    cases["family"] = cases.algorithm.map(family)
    cases["default"] = [DEFAULT[t] == (o, tp, s) for t, o, tp, s in
                        zip(cases.toolchain, cases.opt_level, cases.topology, cases.seed)]
    check(bool((cases.case_id == cases.run + "/" + cases.toolchain + "__" + cases.circuit_id
                + "__r" + cases.rep).all()),
          "case_id is <run>/<tc>__<circuit>__r<rep>")
    check(cases.algorithm.nunique() == 35 and cases.circuit_id.nunique() == 337,
          "35 algorithms and 337 circuits")
    gone = sorted(set(man.circuit_id) - set(cases.circuit_id))
    check(gone == ["shors_nine_qubit_code_indep_n034"]
          and man.set_index("circuit_id").num_qubits.get(gone[0] if gone else "") == "34",
          "the one manifest circuit not in the log is shors_nine_qubit_code_indep_n034 "
          "(34 qubits)")

    print("\nD1: cells (toolchain, opt_level, topology, seed)")
    cells = cases.groupby(CELL).agg(runs=("run", "nunique"), circuits=("circuit_id", "nunique"))
    per_tc = cells.groupby(level="toolchain").size().to_dict()
    print(cells.groupby(level="toolchain").agg(
        cells=("circuits", "size"), circuits=("circuits", lambda s: f"{s.min()}-{s.max()}"))
        .to_string())
    check(len(cells) == 51 and per_tc == {"qiskit": 36, "cirq": 6, "bqskit": 7,
                                          "pennylane": 1, "kirin": 1},
          "51 cells: qiskit 36, cirq 6, bqskit 7, pennylane 1, kirin 1")
    values = {"qiskit": ("0 1 2 3", "all grid line", "1 2 42"),
              "cirq": ("1 converge", "all grid line", "42"),
              "bqskit": ("1 2 3", "all grid line", "1 2 42"),
              "pennylane": ("default", "grid", "42"), "kirin": ("default", "grid", "42")}
    for tc, want in values.items():
        c = cases[cases.toolchain == tc]
        got = tuple(" ".join(sorted(set(c[k]))) for k in CELL[1:])
        check(got == want, f"{tc}: opt_level {want[0]} | topology {want[1]} | seed {want[2]}")
    one = (cases.drop_duplicates(["run", "toolchain"] + CELL[1:])
           .groupby(["run", "toolchain"]).size())
    check(bool((one == 1).all()), "each run holds one cell per toolchain")
    check(cases.run.nunique() == 52
          and sorted(set(cases.toolchain[cases.run == "v1"])) == ["bqskit", "cirq",
                                                                   "pennylane", "qiskit"],
          "52 runs; v1 holds qiskit, cirq, pennylane and bqskit (no kirin)")
    d, f = cases[cases.default], cases[~cases.default]
    check(d.groupby("toolchain").run.nunique().to_dict()
          == {"qiskit": 2, "cirq": 2, "bqskit": 2, "pennylane": 2, "kirin": 1},
          "default cells pool v1 and an -ext run (kirin: kirin-fixpoint only)")
    check(bool((d.groupby("toolchain").circuit_id.nunique() == 337).all()),
          "every default cell has all 337 circuits")
    fc = f.groupby(CELL).agg(circuits=("circuit_id", "nunique"), runs=("run", "nunique"),
                             core=("selection_tier", lambda s: set(s) == {"CORE"}),
                             reps=("rep", lambda s: " ".join(sorted(set(s))))).reset_index()
    b = fc[fc.toolchain == "bqskit"]
    check(len(b) == 6 and bool((b.circuits == 176).all()) and bool(b.core.all()),
          "bqskit's 6 factor cells have the 176 CORE circuits only")
    check(bool((fc[fc.toolchain != "bqskit"].circuits == 337).all()),
          "every other factor cell has all 337 circuits")
    check(bool((fc.runs == 1).all()) and bool((fc.reps == "0").all()),
          "every factor cell is one run with one timing repetition (rep 0)")
    reps = d.groupby(["toolchain", "selection_tier"]).rep.agg(lambda s: " ".join(sorted(set(s))))
    want = {(t, s): "0" if t in ("bqskit", "pennylane") and s == "EXTENDED" else "0 1 2"
            for t in TOOLCHAINS for s in ("CORE", "EXTENDED")}
    check(reps.to_dict() == want, "default cells: repetitions 0-2, except rep 0 only for "
                                  "bqskit and pennylane on the EXTENDED circuits")
    widths = sorted({int(n) for n in cases.num_qubits})
    spare = [n for n in widths if device_qubits(n, "grid") > n]
    check(device_qubits(7, "grid") == 9 and device_qubits(32, "grid") == 36
          and 2 * len(spare) > len(widths)
          and all(device_qubits(n, t) == n for n in widths for t in ("line", "all")),
          f"D2: grid devices have spare qubits for {len(spare)} of the {len(widths)} widths "
          "(7 -> 9, 32 -> 36), line and all devices for none")

    print("\nD6: memory")
    check(bool((ev.mem_peak_bytes == "").all()), "mem_peak_bytes is empty in every pass event")
    check(set(cases.rep) == {"0", "1", "2"},
          "rep is 0-2 only: no memory repetition (rep 3) in the merged log")

    print("\nSection 3.2: event columns")
    tc = ev.toolchain.astype(str)
    stage = ev.stage.astype(str)
    check(sorted(set(stage)) == STAGES, "11 stages")
    kind = ev.pass_kind.astype(str)
    check(bool(((stage == "control") <= (tc == "bqskit")).all())
          and bool(((stage == "control") == (kind == "container"))[tc == "bqskit"].all()),
          "stage control = BQSKit's container events, nothing else")
    smap = read_csv(stage_map, dtype=str)
    check(set(smap.status) == {"suggested"} and set(smap.stage) <= set(STAGES),
          f"every mapping in pass_stage_map.csv ({len(smap)} rows) is still suggested")
    own = (kind != "rewrite_iteration").to_numpy()  # rewrite iterations inherit their stage
    unmapped = sorted(set(zip(tc[own], ev.activity[own].astype(str)))
                      - set(zip(smap.toolchain, smap.activity)))
    if unmapped:
        print(f"  note  {len(unmapped)} passes of the log are not in this {len(smap)}-row "
              f"pass_stage_map.csv (the log was merged with the 86-row map): {unmapped}")
    vocab = {t: set(ev.activity[tc == t].astype(str)) for t in TOOLCHAINS}
    check(all(not vocab[a] & vocab[b] for i, a in enumerate(TOOLCHAINS)
              for b in TOOLCHAINS[i + 1:]),
          "pass vocabularies do not overlap across toolchains")
    kinds = {t: " ".join(sorted(set(kind[tc == t]))) for t in TOOLCHAINS}
    check(kinds == {"qiskit": "analysis transformation", "cirq": "router transformer",
                    "pennylane": "transform", "bqskit": "container pass",
                    "kirin": "configured internal rewrite_iteration"},
          "pass_kind values per toolchain (section 3.3)")
    depth = pd.to_numeric(ev.nesting_depth.astype(str)).groupby(tc).max().to_dict()
    check(depth == {"bqskit": 12, "cirq": 1, "kirin": 4, "pennylane": 0, "qiskit": 0},
          "maximum nesting depth: bqskit 12, kirin 4, cirq 1, pennylane 0, qiskit 0")
    check(bool(ev.parent_activity[tc == "qiskit"].astype(str).str.startswith("stage:").all()),
          "every Qiskit parent_activity is a native stage name (stage:...)")
    blank = (ev.ir_changed.astype(str) == "").groupby(tc).sum().to_dict()
    check(blank == {"bqskit": 0, "cirq": 0, "kirin": 96, "pennylane": 0, "qiskit": 0},
          "ir_changed is blank only for 96 Kirin events")
    ok = ev[ev.status == "ok"]
    q = ok[ok.toolchain == "qiskit"]
    levels = lambda a: sorted(set(q.opt_level[q.activity == a].astype(str)))
    check(levels("FixedPoint") == ["1", "2"] and levels("MinimumPoint") == ["3"],
          "Qiskit: FixedPoint at O1 and O2, MinimumPoint at O3, neither at O0")
    c = ok[ok.toolchain == "cirq"]
    most = (pd.to_numeric(c.iteration)
            .groupby([c.opt_level.astype(str).to_numpy(), c.case_id.to_numpy()]).max())
    p1, conv = most.loc["1"], most.loc["converge"]
    check(bool((p1 == 3).all()) and conv.median() == 7 and conv.max() == 14,
          "Cirq: the most-repeated transformer of a case runs 3 times at opt_level 1, "
          "a median of 7 and at most 14 times at converge")

    print("\nD3: circuits with status ok / circuits, default cell, rep 0")
    d0 = cases[cases.default & (cases.rep == "0")]
    cov = (d0.groupby(["family", "toolchain"]).status
           .agg(lambda s: f"{int((s == 'ok').sum())}/{len(s)}").unstack()[TOOLCHAINS])
    print(cov.to_string())
    check({fam: " ".join(row) for fam, row in cov.iterrows()} == {
        "arithmetic": "56/56 56/56 51/56 39/56 30/56",
        "dynamic": "21/32 3/32 3/32 3/32 3/32",
        "oracle": "40/40 40/40 28/40 21/40 31/40",
        "qft_qpe": "64/64 64/64 62/64 59/64 57/64",
        "random": "14/14 7/14 13/14 2/14 1/14",
        "state_prep": "41/41 41/41 41/41 41/41 41/41",
        "variational": "90/90 90/90 90/90 90/90 90/90"}, "coverage table of D3")
    dyn = d0[d0.family == "dynamic"]
    check(sorted(set(dyn.circuit_id[(dyn.toolchain != "qiskit") & (dyn.status == "ok")]))
          == ["seven_qubit_steane_code_indep_n013", "seven_qubit_steane_code_indep_n026",
              "shors_nine_qubit_code_indep_n017"],
          "outside Qiskit, the dynamic circuits that compile are the 3 QEC circuits")
    b3 = d0[d0.portability_tier == "B"]
    qb = b3[b3.toolchain == "qiskit"]
    check(len(qb) == 29 and int((qb.status == "ok").sum()) == 18
          and bool((b3.status[b3.toolchain != "qiskit"] != "ok").all()),
          "the 29 OpenQASM 3 circuits: 18 compile in Qiskit, none in another toolchain")

    print("\nD4: circuits per family and size bin")
    circ = cases.drop_duplicates("circuit_id")
    size = pd.cut(circ.num_qubits.astype(int), bins=SIZE_BINS, labels=SIZE_LABELS).astype(str)
    check(bool((size != "nan").all()), "every circuit falls in a size bin")
    ct = pd.crosstab(circ.family, size).reindex(columns=SIZE_LABELS, fill_value=0)
    print(ct.to_string())
    check(ct.sum().tolist() == [96, 126, 70, 45], "circuits per size bin: 96, 126, 70, 45")
    check(bool((ct > 0).all().all()), "every family has circuits in every size bin")
    return cases


def check_runs(results, cases):
    print(f"\nRun folders under {os.path.relpath(results, ROOT)} (D2, D6)")
    # the runs merged into merged_v2: v1 without Kirin, and every folder under v2/
    specs = [("v1", results, ["qiskit", "cirq", "pennylane", "bqskit"])]
    specs += [(os.path.basename(os.path.normpath(p)), p, None)
              for p in sorted(glob.glob(os.path.join(results, "v2", "*", "")))]
    check(len(specs) == 52, f"{len(specs)} run folders (52 expected: v1 and 51 under v2/)")
    raw, lacking = [], {}
    for name, path, tcs in specs:
        c = read_csv(os.path.join(path, "cases.csv"), dtype=str)
        lacking.update({name: [k for k in C_COLS if k not in c.columns]})
        raw.append((c[c.toolchain.isin(tcs)] if tcs else c).assign(run=name))
    raw = pd.concat(raw, ignore_index=True)
    check(not any(lacking.values()),
          "every run folder's cases.csv has all the columns the document marks C")
    mem = raw[raw.mem_traced == "True"]
    check(len(raw) == 20310 and len(mem) == 1363,
          f"{len(raw):,} cases, {len(mem):,} of them memory repetitions "
          "(20,310 and 1,363 expected)")
    check(set(mem.rep) == {"3"}, "every memory repetition has rep 3")
    check(mem.toolchain.value_counts().to_dict()
          == {"qiskit": 337, "cirq": 337, "kirin": 337, "pennylane": 176, "bqskit": 176},
          "memory repetitions: qiskit, cirq and kirin 337 each, pennylane and bqskit 176")
    check(set(mem.run) == {"v1", "qiskit-L2-grid-s42-ext", "cirq-p1-grid-ext",
                           "kirin-fixpoint"},
          "memory repetitions exist only in the runs of default cells")
    want = np.array([device_qubits(int(n), t) for n, t in zip(raw.num_qubits, raw.topology)])
    check(bool((raw.device_qubits.astype(int).to_numpy() == want).all()),
          f"device_qubits follows from topology and num_qubits in all {len(raw):,} cases")
    keyed = raw.assign(case_id=raw.run + "/" + raw.case_id)[["case_id", "run_token",
                                                             "mem_traced"]]
    j = cases[["case_id", "run_token"]].merge(keyed, on=["case_id", "run_token"], how="left")
    check(len(j) == len(cases) and bool((j.mem_traced == "False").all()),
          "every merged case is a timing case of a run folder, none a memory repetition")

    has = {}  # (toolchain, pass_kind) -> [events, events with mem_peak_bytes]
    for name, path, _ in specs:
        m = mem[mem.run == name]
        for tc in sorted(set(m.toolchain)):
            e = read_csv(os.path.join(path, f"events_{tc}.csv"), dtype=str,
                         usecols=["case_id", "run_token", "pass_kind", "mem_peak_bytes"])
            e = e.merge(m[m.toolchain == tc][["case_id", "run_token"]],
                        on=["case_id", "run_token"])
            for kind, g in e.groupby("pass_kind"):
                n, k = has.get((tc, kind), (0, 0))
                has[(tc, kind)] = (n + len(g), k + int((g.mem_peak_bytes != "").sum()))
    for (tc, kind), (n, k) in sorted(has.items()):
        print(f"  {tc:10s} {kind:18s} {k:7d} of {n:7d} events have mem_peak_bytes")
    every = lambda tc: all(k == n for (t, _), (n, k) in has.items() if t == tc)
    check(all(k == 0 for (t, _), (_, k) in has.items() if t == "bqskit"),
          "BQSKit records no memory")
    check(all(every(t) for t in ("qiskit", "cirq", "pennylane")),
          "Qiskit, Cirq and PennyLane record memory on every event of a memory repetition")
    kirin = {kind: nk for (t, kind), nk in has.items() if t == "kirin"}
    check(set(kirin) == {"configured", "internal", "rewrite_iteration"}
          and all(n == k for kind, (n, k) in kirin.items() if kind != "rewrite_iteration")
          and kirin["rewrite_iteration"][1] == 0,
          "Kirin records memory on configured and internal passes, not on rewrite iterations")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", default=os.path.join(ROOT, "results", "merged_v2", "event_log.csv"))
    ap.add_argument("--manifest", default=os.path.join(ROOT, "qcm-corpus-v1", "manifest.csv"))
    ap.add_argument("--families",
                    default=os.path.join(ROOT, "paper1", "docs", "circuit_families.csv"))
    ap.add_argument("--stage-map", default=os.path.join(ROOT, "pass_stage_map.csv"))
    ap.add_argument("--runs", nargs="?", const=os.path.join(ROOT, "results"), default=None,
                    metavar="RESULTS", help="also check the run folders (default: results/)")
    args = ap.parse_args()
    man = read_csv(args.manifest, dtype=str)
    fam = read_csv(args.families, dtype=str)
    family = check_families(man, fam)
    cases = check_log(args.log, man, family, args.stage_map)
    if args.runs:
        check_runs(args.runs, cases)
    print(f"\n{len(FAILED)} check(s) failed" if FAILED else "\nall checks passed")
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
