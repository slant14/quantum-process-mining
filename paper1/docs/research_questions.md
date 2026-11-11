# Paper 1: research questions and their terms in the log

**Status: proposal for the freeze (issue #2).** Every team member approves the pull
request that adds this file; that approval freezes it. After the freeze, any change to an
RQ needs its own issue. Still open: the wording points in §1.4 and the proposals D1–D6
in §4.

**Sources.** The RQs, measures and scope lists are copied from the Paper 1 plan,
`README_Paper1_Behavioral_Waste_Characterization.md` ("the plan"). Statements about the
data refer to the merged v2 log `results/merged_v2/event_log.csv` (Zenodo record
23614607), the corpus manifest `qcm-corpus-v1/manifest.csv`, and the 52 run folders the
log was merged from. `paper1/scripts/check_rq_terms.py` checks each of these statements
and prints the tables in §4:

```bash
.venv/bin/python paper1/scripts/check_rq_terms.py          # merged log, manifest, families
.venv/bin/python paper1/scripts/check_rq_terms.py --runs   # also the run folders (Git LFS)
```

`#N` is GitHub issue N of the milestone *Week 1 - Behavioral paper* (the issues also
write W1-NN, for example W1-04 for #4).

## 1. Research questions

### 1.1 RQ1: Behavioral structure

**How do quantum compiler pipelines behave at runtime, and how does their observed
control flow vary across toolchains, compiler configurations, architectures, and circuit
families?**

### 1.2 RQ2: Redundant work

**How much compilation cost is attributable to ineffective transformation passes,
redundant analysis executions, and unproductive fixpoint iterations, and how does this
vary across passes, stages, circuit families, configurations, and toolchains?**

We must distinguish:

1. **Ineffective transformation execution**: a transformation pass runs but does not
   produce a relevant IR change;
2. **Redundant analysis execution**: an analysis is recomputed even though the relevant
   compiler state has not changed;
3. **Unproductive fixpoint iteration**: an iteration performs no useful change and exists
   only to establish convergence.

**IR unchanged != automatically waste.** Analysis passes may intentionally leave the IR
unchanged.

### 1.3 RQ3: Concentration and stability

**Where is redundant compilation work concentrated, and how stable are the observed
behavioral and waste patterns across circuits, configurations, and corpus subsamples?**

### 1.4 Wording points to settle before approval

1. **Proposed change: name architectures in RQ2 and RQ3.** RQ1 lists "compiler
   configurations, architectures" as two dimensions. RQ2 and RQ3 list only
   "configurations", yet the plan reports no-op rates by architecture (Task 5.2) and tests
   stability across architectures (Task 6.3), and its scope list has "comparison across
   architectures". With "configuration" meaning the compiler setting (D1), RQ2 and RQ3
   would not cover architectures. Proposed wording:
   - RQ2: "... and how does this vary across passes, stages, circuit families,
     configurations, architectures, and toolchains?"
   - RQ3: "... across circuits, configurations, architectures, and corpus subsamples?"
2. **Reading, no change: "redundant" in RQ2.** Where the log cannot show that the relevant
   state was unchanged, the answer reports *repeated* analysis executions, not redundant
   ones (plan, Task 2). #8 decides for each toolchain which word may be used.
3. **Reading, no change: "redundant compilation work" in RQ3** covers all three RQ2
   categories, not only redundant analysis.
4. **Reading, no change: "circuits" in RQ3** covers both circuit families (Task 6.1) and
   resampling of circuits (Task 6.4).

## 2. Measures and where they are shown

The output IDs follow the plan's *Minimum Required Figures* (F1–F7) and *Minimum
Required Tables* (T1–T6). The plan's RQ output lists ask for four more tables, numbered
T7–T10 here. Which outputs move to an appendix is decided in week 3.

| ID | Output | RQ | Plan source |
|---|---|---|---|
| F1 | Research and instrumentation pipeline | – | min. figure 1 |
| F2 | Representative DFG per major toolchain | 1 | min. figure 2; RQ1 output 1 |
| F3 | Process-variant comparison | 1 | min. figure 3 |
| F4 | Transformation no-op (ineffective-pass) distribution | 2 | min. figure 4; RQ2 output 3 |
| F5 | Wasted-runtime concentration | 2, 3 | min. figure 5 |
| F6 | Fixpoint iteration behavior | 1, 2 | min. figure 6; RQ2 output 4 |
| F7 | Stability across dataset size and configurations | 3 | min. figure 7; RQ3 output 2 |
| T1 | Dataset and toolchain summary | – | min. table 1; Task 3 (#12) |
| T2 | Event-log schema | – | min. table 2 (#14) |
| T3 | Top process variants | 1 | min. table 3; RQ1 output 2 |
| T4 | Pass-level waste summary, with the wasted-runtime ranking | 2 | min. table 4; RQ2 outputs 1, 2 |
| T5 | Toolchain-level RQ2 comparison | 2 | min. table 5; RQ2 output 6 |
| T6 | Stability and robustness summary, with the circuit-family and configuration/backend comparisons | 3 | min. table 6; RQ3 outputs 1, 3, 4 |
| T7 | Loops and fixpoint rounds | 1, 2 | RQ1 output 3 |
| T8 | Nesting | 1 | RQ1 output 4 |
| T9 | Declared vs observed execution (example) | 1 | RQ1 output 5 |
| T10 | Repeated analysis | 2 | RQ2 output 5 |

"Needs" names the issue or decision that a measure depends on. §3 maps the terms to
columns.

### RQ1

| Measure (plan) | Shown in | Computed from | Needs |
|---|---|---|---|
| Executed pass sequences | F2, T3 | traces (§3.2) | #4 |
| Directly-follows relations | F2, plus full edge lists as CSV | consecutive event pairs of a trace | #4, #13 |
| Process variants: number of unique variants, frequency of the top variants, share of cases covered by the top 1, 5 and 10 | T3, F3 | distinct traces per cell (D1) | #3, #4 |
| Trace length, average and median | T1, T3 | events per trace | #4 |
| Loops and repeated passes: repeated activities, self-loops, repeated pass groups, fixpoint iteration counts and their distribution | T7, F6 | `iteration`; `loop_id`, `round_index` | #10 |
| Nested pass execution: nesting depth, nested pass frequency, parent–child relations, configured vs executed passes | T8 | `nesting_depth`, `parent_activity`, `is_container` | #11 |
| Conditional pass behavior | T9, F2 | share of a cell's cases in which an activity runs | #11 |
| Declared vs observed execution: a configured pass never runs, a nested pass runs without being configured, a pass repeats more often than the configuration suggests | T9 | `top` traces vs `paper1/docs/declared_pipelines.md` | #11 |
| Models per optimization level, architecture and circuit family (Task 4.1) | F3, T6 | the measures above per subgroup | D1, D2, D3 |

### RQ2

| Measure (plan) | Shown in | Computed from | Needs |
|---|---|---|---|
| Per pass: executions, IR-changing executions, unchanged executions, total runtime, runtime of unchanged executions (Task 5.1) | T4 | `activity`, `ir_changed`, `duration_ns` | #4, #9 |
| Per pass: total memory and memory of unchanged executions, where available (Task 5.1) | T4 | `mem_peak_bytes` of the memory repetitions | D6 |
| Transformation no-op rate = unchanged transformation executions / all transformation executions, by toolchain, pass, stage, circuit family, configuration and architecture (Task 5.2) | F4; T4 per pass; T5 per toolchain | `pass_category`, `ir_changed`, the grouping columns | #7, #8, #9 |
| Repeated analysis: executions, repeat count, time in repeated executions, whether the relevant state changed in between (Task 5.3) | T10 | `pass_category`, `iteration`, `ir_changed` of the events in between, `duration_ns` | #7, #8, #9 |
| Fixpoint loops: total, productive and unproductive iterations, runtime per iteration, cost of the final confirming iteration, share of loop time in non-changing rounds (Task 5.4) | F6, T7 | `loop_id`, `round_index`, `is_confirming_round`, `ir_changed`, `duration_ns` | #8, #10 |
| Cost concentration: top 5 passes by wasted runtime, share of wasted runtime from the top 10 % of passes, stages with the most unchanged work (Task 5.5) | F5, T4 | waste flags, `duration_ns`, `activity`, `stage` | #8 |
| Toolchain-level summary | T5 | the measures above per `toolchain` | – |

### RQ3

| Measure (plan) | Shown in | Computed from | Needs |
|---|---|---|---|
| Which passes account for most wasted time | F5, T4 | as cost concentration (RQ2) | #8 |
| Whether the same passes repeatedly appear ineffective | T6 | per-pass no-op rate per subgroup and subsample | #8 |
| Whether loop behavior is stable | T6, F7 | round counts per subgroup and subsample | #10 |
| Whether findings persist across circuit families (Task 6.1) | T6 | the headline RQ1 and RQ2 measures per `family` | D3 |
| Whether findings persist across optimization levels (Task 6.2) | T6, F7 | the same per `opt_level` | D1 |
| Whether findings persist across architectures, as a structural or an intensity difference (Task 6.3) | T6, F7 | the same per `topology` | D2 |
| Whether the discovered process structure is stable when the dataset is resampled: major DFG edges, top waste-producing passes, no-op estimates, loop distributions at 25, 50, 75 and 100 % (Task 6.4) | F7 | circuit subsamples | D5 |
| Sensitivity to abstraction: native pass names vs coarse stages (Task 6.5) | T6 | `activity` vs `stage` | review of the stage map |

## 3. Terms and log columns

Where a column comes from:

- **E**: a column of `event_log.csv` (34 columns). Case attributes are repeated on every
  event of a case; read them from its outcome event (`phase == "outcome"`, exactly one per
  case).
- **C**: a case column of the run folders' `cases.csv` that `event_log.csv` does not
  have: `device_qubits`, `mem_traced`, `compile_ms`, `load_ms`, `n_events`, `out_ops`,
  `out_2q_ops`, `versions`, `finished_utc`, `input_format`, `barriers_stripped`.
  (`merge_logs.py` copies some of them to the `compilation` objects of
  `event_log.ocel.sqlite`.)
- **M**: `qcm-corpus-v1/manifest.csv`, joined on `circuit_id` or `algorithm`.
- **F**: a mapping file in `paper1/docs/`.
- **D**: a column derived in week 1, by the issue named.

### 3.1 Terms that need a decision

| Term in the RQs | RQ | Log columns | Decision |
|---|---|---|---|
| Toolchain | 1, 2 | `toolchain` (E): `qiskit`, `cirq`, `pennylane`, `bqskit`, `kirin` | none |
| Configuration | 1, 2, 3 | `opt_level` (E), within a cell (`toolchain`, `opt_level`, `topology`, `seed`); `run` (E) is provenance only | D1 |
| Architecture / backend | 1 (2, 3: see §1.4) | `topology` (E); `device_qubits` (C) follows from `topology` and `num_qubits` | D2 |
| Circuit family | 1, 2, 3 | `algorithm` (E) → `family` (F: `circuit_families.csv`) | D3 |
| Circuit size | (3) | `num_qubits` (E) → `size_bin` | D4 |
| Corpus subsamples | 3 | subsets of `circuit_id` (E) | D5 |
| Compilation cost: memory | 2 | `mem_peak_bytes`, memory repetitions only | D6 |

### 3.2 The other terms

| Term | RQ | Maps to | Notes |
|---|---|---|---|
| Compiler pipeline | 1 | one toolchain in one cell (D1) | |
| Case, compilation | all | `case_id` (E): `<run>/<tc>__<circuit>__r<rep>` | key and repetition rules: #3 |
| Behavior at runtime, observed control flow, executed pass sequence (**trace**) | 1 | `activity` (E) ordered by `event_index` (E) within a `case_id`, outcome events left out, in one view: `full`, `leaf` or `top` | views: #4. Order by `event_index`, never by timestamp (README convention 1). |
| Pass | 1, 2, 3 | `activity` (E) within one `toolchain`, with `activity_module` (E) where a name collides | vocabularies do not overlap across toolchains. Kirin's `Fixpoint[<rules>]`: `activity_base`, `fixpoint_rules` (D, #4) |
| Directly-follows relation | 1 | two consecutive events of a trace | |
| Process variant | 1 | a distinct trace within one cell | |
| Trace length | 1 | the number of events in a trace | depends on the view |
| Repeated pass, loop | 1 | `iteration` (E): how many times the activity has run so far in the case. Self-loop: the same activity twice in a row. | `iteration` is not a loop round (#10) |
| Fixpoint iteration (round) | 1, 2 | `loop_id`, `round_index`, `is_confirming_round` (D, #10), derived from Qiskit's `FixedPoint` loop (O1, O2) or `MinimumPoint` loop (O3; neither at O0), Kirin's events with `pass_kind == "rewrite_iteration"`, Cirq at `opt_level == "converge"`, and BQSKit's repetitions if #10 finds loops there | at `converge`, Cirq's most-repeated transformer runs a median of 7 (at most 14) times per case, against 3 at `opt_level == "1"`, so #10 has to cover Cirq too |
| Nested pass execution | 1 | `nesting_depth`, `parent_activity`, `is_container` (E) | maximum depth: BQSKit 12, Kirin 4, Cirq 1, PennyLane and Qiskit 0. Qiskit's `parent_activity` is its native stage (`stage:layout`, ...), not an event (#11) |
| Conditional pass behavior | 1 | the share of a cell's cases in which an activity runs, where it is below 100 % | |
| Declared pipeline | 1 | `paper1/docs/declared_pipelines.md` (F, #11), compared with the `top` view | |
| Compilation cost: time | 2 | `duration_ns` (E, tracing overhead subtracted), summed over leaf events, timing repetitions only | not `compile_ms` (C), which includes tracer overhead. Time rules: #8 |
| Attributable cost | 2 | the leaf `duration_ns` of the events flagged as waste, also as a share of all leaf `duration_ns` in the same group | #8 |
| Transformation, analysis, checking/control pass | 2 | `pass_category` (D) from `paper1/docs/pass_taxonomy.csv` (F, #7) | not `pass_kind`, whose values differ per toolchain, and not `stage` |
| IR change | 2 | `ir_changed` with `changed_method` (E) | one method per toolchain, verdict from #9; blank for 96 Kirin events. `size_before` and `size_after` are only a proxy (Kirin counts IR statements). |
| Ineffective transformation (no-op) | 2 | a transformation with `ir_changed == False` | #8 |
| Repeated, redundant analysis | 2 | repeated: an analysis whose activity already ran in the case. Redundant: repeated, and no event in between has `ir_changed == True`. | "redundant" only where #9 shows that `ir_changed` follows the running state (#8) |
| Unproductive fixpoint iteration | 2 | a round without an `ir_changed == True` event | the confirming round is reported as confirmation cost, not as waste (#8) |
| Stage | 2, 3 | `stage` (E): 11 stages from `pass_stage_map.csv` | a rewrite iteration takes the stage of its pass; `control` holds BQSKit's containers and nothing else; every mapping is still `suggested`. The log was merged with an 86-row map; the repository has 80 rows until #1 pushes the newer file. Not Qiskit's native stage in `parent_activity`. |
| Redundant compilation work | 3 | the union of the three RQ2 categories, confirmation cost excluded | §1.4 |
| Concentrated | 3 | the share of wasted leaf time from the top 5 passes and from the top 10 % of passes, per toolchain; the same per `stage` | |
| Circuits | 3 | `circuit_id` (E): the 337 compiled circuits | the manifest's 338th circuit, `shors_nine_qubit_code_indep_n034` (34 qubits), was not compiled (limit 32 qubits) |
| Behavioral patterns | 3 | the RQ1 measures | |
| Waste patterns | 3 | the RQ2 measures | |
| Stable | 3 | a pattern's summary agrees across subgroups and subsamples | the agreement statistics are fixed in week 3. Proposal: Jaccard index of DFG edge sets, overlap of the top-5 waste passes, spread of no-op rates. |

### 3.3 Columns to avoid for these terms

- The manifest's `level`, `opt_level` and `seed` (M) describe how MQT Bench generated the
  circuits (level `indep` at opt level 0, except `shor_alg_n018` at level `alg`; seed 42
  for the 28 seeded circuits). They are not compiler settings. Drop them before joining
  the manifest to the log.
- `iteration` counts occurrences, not loop rounds (#10).
- `pass_kind` records how the tracer saw a pass (Qiskit `analysis`/`transformation`, Kirin
  `configured`/`internal`/`rewrite_iteration`, BQSKit `container`/`pass`). It is not the
  pass category (#7).
- `run` is a folder, not a configuration. `v1` holds four toolchains, and the default
  cell of Qiskit, Cirq, BQSKit and PennyLane is split over `v1` (CORE circuits) and an
  `-ext` run (EXTENDED circuits).
- `compile_ms` (C) includes tracer overhead; `duration_ns` does not.
- `device_qubits` (C) is not a separate factor (D2).
- `selection_tier` decides which cells a circuit appears in: BQSKit's factor runs cover the
  CORE circuits only (D1).

## 4. Decisions (proposals)

### D1: Configuration

1. A **cell** is one combination of `toolchain`, `opt_level`, `topology` and `seed`. The
   log has 51 cells. These are the "51 configurations" of the dataset README, with the
   same key as the OCEL `configuration` object.

   | `toolchain` | `opt_level` | `topology` | `seed` | Cells | Design | Circuits per cell | Timing repetitions |
   |---|---|---|---|---:|---|---|---|
   | qiskit | 0, 1, **2**, 3 | **grid**, line, all | **42**, 1, 2 | 36 | full factorial | 337 | 3 in the default cell, 1 elsewhere |
   | cirq | **1**, converge | **grid**, line, all | 42 | 6 | full factorial | 337 | 3 in the default cell, 1 elsewhere |
   | bqskit | **1**, 2, 3 | **grid**, line, all | **42**, 1, 2 | 7 | one factor at a time around the default | 337 in the default cell, 176 (CORE) elsewhere | default cell: 3 (CORE), 1 (EXTENDED); 1 elsewhere |
   | pennylane | default | grid | 42 | 1 | – | 337 | 3 (CORE), 1 (EXTENDED) |
   | kirin | default | grid | 42 | 1 | – | 337 | 3 |

   Bold marks the toolchain default. `opt_level` holds Qiskit's and BQSKit's optimization
   level and Cirq's `max_num_passes` (`converge`: repeat until nothing changes). PennyLane
   and Kirin have no setting.
2. `run` is not part of the key. The two runs that hold a default cell (`v1` and the
   `-ext` run) are pooled. Each factor run is a cell of its own, because it changes exactly
   one key column.
3. In the RQs, **configuration** is the `opt_level` factor and **architecture** is
   `topology` (D2). `seed` is not a configuration contrast. Only Qiskit and BQSKit read it
   (`toolchains/qiskit/run_corpus.py:135-140`, `toolchains/bqskit/run_corpus.py:95`).
   Differences between cells that differ only in `seed` are reported as seed variability
   (RQ1) and used as a robustness check (RQ3). In Qiskit the seed also changes the
   synthetic calibration data of the `GenericBackendV2` target, so a Qiskit seed
   difference mixes randomness with a different backend.
4. A contrast varies one factor and keeps the others at the toolchain default. BQSKit
   allows only this design, and using it for every toolchain keeps them comparable.
   Interactions in the Qiskit and Cirq factorials are a secondary analysis.
5. All cells of a contrast have the same circuits and the same repetition: the CORE
   circuits for BQSKit, and `rep == 0`, the only timing repetition of a factor run. #3
   freezes the repetition rule.

### D2: Architecture

1. **Architecture** is `topology`: `grid`, `line` or `all` (all-to-all). The devices are
   synthetic: `run_all.py` builds each one from the circuit width (`device()`).
   `device_qubits` is not a separate factor. In all 20,310 cases of the run folders it
   equals `num_qubits` on `line` and `all`, and rows × columns with ⌈√n⌉ columns on
   `grid`. It is not in `event_log.csv`.
2. Architectures are compared only where the pipeline reads the device and more than one
   topology was run: Qiskit, Cirq and BQSKit. PennyLane routes (its `transpile` step takes
   the coupling map) but ran on `grid` only. Kirin ignores the device and has no router.
   Its `topology == "grid"` is a recorded default without effect, and the missing router
   is reported as a finding.
3. The other factors stay at the default (the default `opt_level`, `seed == "42"`), and
   BQSKit uses the CORE circuits.
4. Reading a contrast: `all` needs no routing, so grid or line against all isolates the
   routing work. A grid device has spare qubits for most widths (7 → 9, 32 → 36), and
   line and all have none, so grid against line mixes connectivity with layout freedom.
   Each difference is reported as **structural** (different DFG edges or variants) or as
   an **intensity** difference (same structure, different counts or time), as Task 6.3
   asks.

### D3: Circuit family

`paper1/docs/circuit_families.csv` maps the 35 algorithms to 7 families. Each family is a
union of the manifest's `stress_class` values (13 classes, which `qcm-corpus-v1/README.md`
defines as "which part of a pipeline the circuit exercises"), so no stress class is
split.

| `family` | `stress_class` values | Algorithms | Circuits | CORE |
|---|---|---|---:|---:|
| `state_prep` | entangling-structure, routing-stress | ghz, wstate, graphstate | 41 | 41 |
| `oracle` | oracle-shallow, oracle-decomposition | bv, dj, grover, qwalk | 40 | 26 |
| `qft_qpe` | canonical-dense, canonical-composite, depth-stress | qft, qftentangled, qpeexact, qpeinexact, hhl, shor | 64 | 29 |
| `arithmetic` | arithmetic-synthesis | 9 adders and multipliers | 56 | 10 |
| `variational` | variational, industry-workload | qaoa, qnn, vqe_real_amp, vqe_su2, vqe_two_local, bmw_quark_cardinality, bmw_quark_copula | 90 | 56 |
| `dynamic` | dynamic-control, fault-tolerant | dynamic_qft, ghz_dynamic, iqpe, seven_qubit_steane_code, shors_nine_qubit_code | 32 | 0 |
| `random` | unstructured-control | randomcircuit | 14 | 14 |
| | | 35 | 337 | 176 |

Why these classes are merged:

- graphstate (routing-stress) joins the GHZ and W states: all three prepare a fixed
  entangled state.
- shor (depth-stress, one circuit) joins QFT and QPE: Shor's algorithm is phase
  estimation over modular exponentiation.
- The QUARK cardinality and copula circuits (industry-workload) join the variational
  ansätze, which have the same structure: layers of parameterized rotations (rx, rz) with
  rxx entangling gates. The copula circuits also contain h and cx, and the 2-qubit copula
  circuit has no rxx. Alternative: an eighth family, `industry` (20 circuits, none in
  CORE).
- The QEC codes (fault-tolerant) join dynamic-control: every circuit of these five
  algorithms contains mid-circuit `measure` and classically conditioned gates (`if_else`),
  and no other circuit contains `if_else`. `dynamic` is exactly the set of algorithms with
  `has_dynamic_control == True` in the manifest.

Coverage limits what a family can show. Circuits with status `ok` in each toolchain's
default cell, `rep == 0`:

| `family` | qiskit | cirq | pennylane | bqskit | kirin |
|---|---:|---:|---:|---:|---:|
| arithmetic | 56/56 | 56/56 | 51/56 | 39/56 | 30/56 |
| dynamic | 21/32 | 3/32 | 3/32 | 3/32 | 3/32 |
| oracle | 40/40 | 40/40 | 28/40 | 21/40 | 31/40 |
| qft_qpe | 64/64 | 64/64 | 62/64 | 59/64 | 57/64 |
| random | 14/14 | 7/14 | 13/14 | 2/14 | 1/14 |
| state_prep | 41/41 | 41/41 | 41/41 | 41/41 | 41/41 |
| variational | 90/90 | 90/90 | 90/90 | 90/90 | 90/90 |

Proposals:

- `dynamic` is analyzed within Qiskit only. Outside Qiskit only its 3 QEC circuits
  compile: only Qiskit reads the 29 OpenQASM 3 circuits, and it compiles 18 of them.
- Every family result states its number of circuits. A toolchain–family cell with fewer
  than 10 `ok` circuits is shown but not interpreted.
- A comparison of families across toolchains uses the circuits that compile in every
  toolchain compared (#6 decides how failed cases are treated).
- CORE contains no `dynamic` circuit, so BQSKit's factor runs say nothing about that
  family.

### D4: Circuit size

`size_bin` is computed from `num_qubits` (the actual width, not the manifest's
`requested_size`). Upper bounds are inclusive:

```python
size_bin = pd.cut(num_qubits, bins=[1, 5, 12, 20, 32], labels=["2-5", "6-12", "13-20", "21-32"])
```

The bins hold 96, 126, 70 and 45 circuits, and every family has circuits in every bin.
Size is confounded with family for algorithms that exist only at some widths: grover up
to 10 qubits, qwalk up to 6, hhl up to 10, half_adder up to 7, and multiplier,
rg_qft_multiplier and bmw_quark_copula up to 12; iqpe only at 2,
hrs_cumulative_multiplier only at 5, shor only at 18. Size effects are therefore read
within families.

### D5: Corpus subsamples

The sampling unit is the circuit (`circuit_id`). A subsample keeps every case of its
circuits, in every toolchain and cell, so all toolchains see the same circuits. The
fractions are 25, 50 and 75 % of the 337 circuits (of the 176 CORE circuits for BQSKit's
factor runs), plus the full set. Samples are stratified by `family` with at least one
circuit per family, with 20 draws per fraction and the seeds recorded.

### D6: Memory cost

`results/merged_v2` contains no memory repetitions. `merge_logs.py` drops cases with
`mem_traced == True` unless it is given `--include-mem-reps`, and the release command does
not pass that flag. `mem_peak_bytes` is empty in all 1,754,405 pass events, and
`mem_traced` is not a column of `event_log.csv`. The 1,363 memory repetitions
(`rep == 3`) are in the run folders, in the default cell of each toolchain only: 337
circuits each for Qiskit, Cirq and Kirin, and the 176 CORE circuits for PennyLane and
BQSKit. BQSKit records no memory. Kirin records it for configured and internal passes,
not for rewrite iterations.

Proposal: memory measures come from the memory repetitions in the run folders, or from a
merge with `--include-mem-reps` that also keeps `mem_traced`. They are reported for
Qiskit, Cirq, PennyLane and Kirin in their default cell, never for BQSKit, and never mixed
with timing repetitions. #1 (step 7) and #3 confirm this.

## 5. Scope (copied from the plan)

### In scope

- event-log cleaning;
- event-log validation;
- pass-level instrumentation analysis;
- process discovery;
- Directly-Follows Graphs;
- process variants;
- process trees / Petri nets where useful;
- loop analysis;
- nesting analysis;
- duration analysis;
- memory analysis;
- pass-effect analysis;
- waste characterization;
- comparison across toolchains;
- comparison across configurations;
- comparison across circuit families;
- comparison across architectures;
- stability / robustness analysis;
- declared-vs-observed execution comparison where possible.

### Out of scope

Do NOT add these to Paper 1:

- predicting whether a pass will matter;
- learned skip rules;
- pass guards;
- dynamic pipelines;
- causal claims;
- intervention experiments as a main contribution;
- automatic pass skipping;
- early stopping optimization;
- reinforcement learning;
- genetic algorithms;
- pass-ordering optimization;
- optimal sequence search;
- object-centric process mining;
- circuit-quality optimization.

These belong to later papers.
