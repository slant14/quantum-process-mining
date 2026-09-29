# qcm-pipeline — behavioural event logs from five quantum compilers

Runs the `qcm-corpus-v1` circuits through **Qiskit, Cirq, PennyLane, BQSKit and
Kirin/Bloqade**, records every pass each compiler executes, and merges the result
into one process-mining event log (CSV + XES).

Each compilation is one **case**; each pass execution is one **event**.

## Quick start

```bash
# layout: keep the corpus next to the pipeline
#   work/qcm-corpus-v1/   work/qcm-pipeline/

cd qcm-pipeline
./setup_envs.sh                         # 5 toolchain venvs + 1 merge venv (Python >= 3.11)

python3 run_all.py --dry-run            # how many jobs the default plan has
python3 run_all.py --limit 4 --max-qubits 5 --reps 1 --mem-reps 0 --out results-smoke
python3 run_all.py                      # full run (CORE selection, all tiers, 3+1 reps)

.venv/bin/python merge_logs.py          # -> results/merged/
```

Run the full job inside `tmux` or `screen`. If the laptop sleeps the run pauses; if it
is killed, **re-run the same command** — finished cases are skipped.

**Use Python 3.12 or 3.13.** The floor is 3.11 (cirq-core, pennylane, pandas, pm4py);
3.14 and newer fail, because some dependencies — `pydantic-core`, pulled in via Kirin —
have no 3.14 wheels yet and fall back to compiling Rust with a PyO3 that supports at
most 3.13. `setup_envs.sh` checks this and stops before installing anything.

```bash
brew install python@3.12                 # macOS
sudo apt install python3.12 python3.12-venv   # Ubuntu / Pop!_OS
rm -rf toolchains/*/.venv .venv && PYTHON=python3.12 ./setup_envs.sh
```

## Layout

```
qcm-pipeline/
├── setup_envs.sh           one venv per toolchain, one for merging
├── run_all.py              orchestrator (stdlib only)
├── merge_logs.py           events -> event_log.csv, *_passes.xes, *_stages.xes
├── pass_stage_map.csv      ontology: (toolchain, pass) -> stage   ** review this **
├── requirements.txt        merge env: pm4py, pandas
└── toolchains/<tc>/
    ├── run_corpus.py       worker; self-contained, imports nothing shared
    └── requirements.txt    pinned versions
```

The per-toolchain folders mirror the self-contained layout of `qcompiler-mining`:
`run_corpus.py` can be dropped next to the existing `pass_logger.py` etc. It does not
import them; each worker carries its own tracing code.

## Design decisions (and why)

| Decision | Reason |
|---|---|
| One venv per toolchain | `pennylane-qiskit` pins Qiskit 2.3.0; sharing an env would silently change the Qiskit being measured. |
| Strictly one compilation at a time | Timing and memory are data; parallel runs contaminate both. |
| Jobs shuffled (seed 42) across toolchains | No toolchain always runs first/last (thermal and cache drift). |
| Warm-up compilation discarded on every worker (re)start | First run pays import/JIT/cache costs. |
| `--reps 3` timing + `--mem-reps 1` memory, never mixed | `tracemalloc` roughly triples compile time in the smoke test. |
| Barriers stripped for **every** toolchain (default) | Cirq cannot parse `barrier` (87% of files). Identical bytes go to all five; `input_sha16` proves it. `--keep-barriers` gives the raw coverage run. |
| Each toolchain at its **own default** optimisation level | Qiskit 2, BQSKit 1; Cirq/PennyLane/Kirin have fixed pipelines. Override with `--opt-level '{"qiskit":3}'`. |
| Same device for all: grid coupling map | `--topology grid|line|all`; device = smallest near-square grid ≥ circuit width. |
| Timeout kills the worker's whole process group | BQSKit spawns runtime processes; nothing is left orphaned. |

## What each toolchain runs

| Toolchain | Pipeline | Basis | Routing | Tracing hook |
|---|---|---|---|---|
| Qiskit 2.5.2 | `generate_preset_pass_manager(2)` on `GenericBackendV2` (control flow on) | cz, u | yes | pass-manager callback; Qiskit times passes itself; native stage label per pass |
| Cirq 1.7.0 | `optimize_for_target_gateset(CZ)` → `RouteCQC` → re-target → merge/eject/drop cleanups | CZ + PhasedXZ | yes | `TransformerLogger` (captures nested transformers); router timed explicitly |
| PennyLane 0.45.1 | `decompose` → `transpile(coupling_map)` → `decompose` → `qml.compile`'s default transforms | CNOT, RX, RY, RZ | yes | each transform timed |
| BQSKit 1.2.1 | `build_workflow(opt 1)`, `num_workers=1`, fresh `Compiler()` per circuit | CZ, U3 | yes | every pass at every nesting level (branches, per-block loops) |
| Kirin 0.22.14 / Bloqade 0.15.0 | `QASM2Py` → `QASM2Fold` → `UOpToParallel` | native | **no** | `unsafe_run` wrapped on every `Pass` subclass: unconfigured passes and fixpoint iterations included |

The bases are not identical, by necessity: PennyLane's `decompose` never reaches CZ
from CNOT, and Kirin/Bloqade has no coupling-map router for this input. Both are
recorded, not hidden. For a behavioural study this is acceptable; do not headline
output-quality comparisons.

## Outputs

`results/`
- `cases.csv` — one row per compilation: status (`ok`, `load_error`, `compile_error`,
  `timeout`, `crash`), error text, load/compile ms, output op counts, versions, input hash.
- `events_<toolchain>.csv` — one row per pass execution.
- `logs/worker_<toolchain>.log` — worker stderr.
- `run_config.json` — arguments, host, corpus provenance.

`results/merged/` (from `merge_logs.py`; default: `ok` cases only, memory reps excluded)
- `event_log.csv` — all events + case attributes + `stage`.
- `event_log_passes.xes` — activity = raw pass name. Mine **per toolchain** (filter on
  case attribute `toolchain`); the pass vocabularies do not overlap.
- `event_log_stages.xes` — activity = ontology stage, pure control-flow wrappers
  removed, consecutive repeats collapsed. The **cross-toolchain** view.

Event columns: `event_index` (order within case — sort by this, not timestamp),
`activity`, `activity_module`, `pass_kind`, `nesting_depth`, `parent_activity`
(Qiskit: its native stage), `is_container`, `iteration` (nth occurrence of this pass in
the case), `start_unix_ns`, `duration_ns` (tracing overhead subtracted), `ir_changed`,
`changed_method`, `size_before`, `size_after`, `mem_peak_bytes`.

## Caveats to state in the paper

- **`ir_changed` is defined per toolchain** (`changed_method` column): DAG fingerprint
  (Qiskit), circuit equality (Cirq), tape fingerprint (PennyLane), circuit fingerprint
  (BQSKit), `RewriteResult.has_done_something` (Kirin — "a rewrite fired", which can be
  true even if the net IR is unchanged).
- **Memory** is `tracemalloc` peak: Python heap only. Qiskit's Rust core is invisible
  to it. Exact for leaf passes; for container passes it covers only the time since the
  last child started. BQSKit: not recorded (passes run in runtime worker processes).
- **BQSKit durations** are wall-clock inside its cooperative async runtime; a pass that
  awaits sub-tasks includes interleaved work.
- **Analysis passes never change the IR by design** — use `pass_kind` to separate them
  before reporting a "no-op" rate.

## Coverage findings from the smoke tests

These are results, not bugs in the pipeline:
- Cirq's QASM importer rejects `barrier`; with barriers stripped it still rejects
  Qiskit's 4-parameter `cu`.
- PennyLane has no usable native QASM 2 parser: `qml.from_qasm` requires
  `pennylane-qiskit`, i.e. Qiskit's parser. The native `from_qasm3` rejects `include`.
- BQSKit's default workflow refuses gates wider than `max_synthesis_size=3`
  (e.g. `dj_indep_n004`).
- Bloqade's `QASM2Py` does not convert the `pi` constant, so the parallelisation
  analysis fails on circuits using it — a candidate upstream issue.
- `qiskit-qasm3-import` does not support the `^` operator (`ghz_dynamic_indep_n005`).
- Only Qiskit can compile the QASM3-only (Tier B) circuits.

## Runtime

The full run is dominated by BQSKit (2–6 s per small circuit in the smoke test vs.
milliseconds for the others; synthesis grows steeply with width). Use `--dry-run` for
the job count, run a smoke test first, and plan it as an overnight job. `--timeout`
(default 600 s) bounds the worst case per compilation.

## Licences

pm4py is AGPL-3.0 (fine for research; relevant if merged into a commercial product).
Toolchains keep their own licences. Cite MQT Bench for the corpus.
