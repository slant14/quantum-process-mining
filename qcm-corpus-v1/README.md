# qcompiler-mining input circuit corpus — v1

Fixed, versioned set of **352 quantum circuits across 36 algorithms**, used as the
common input to every toolchain in the `qcompiler-mining` study. The corpus is
toolchain-neutral: Qiskit is only the *generator*, every artifact on disk is plain
OpenQASM.

**Source:** MQT Bench — Quetschlich, Burgholzer, Wille, *MQT Bench: Benchmarking
Software and Design Automation Tools for Quantum Computing*, Quantum 7:1062 (2023).
Generated with `mqt-bench 2.3.0` / `qiskit 2.5.2`. Full provenance in
`provenance.json`.

## Layout

```
qcm-corpus-v1/
├── qasm2/<algorithm>/<algorithm>_<level>_n<NNN>.qasm    309 files
├── qasm3/<algorithm>/<algorithm>_<level>_n<NNN>.qasm    352 files
├── manifest.csv          one row per circuit, 35 columns
├── generation_log.csv    every failed attempt with its reason
├── provenance.json       versions, seeds, ladder, caps, host
└── scripts/              the exact generator + validator used
```

Naming: `{algorithm}_{level}_n{qubits:03d}.qasm` — zero-padded so lexical order is
numeric order. `num_qubits` is the **actual** width; the requested size is kept
separately in the manifest because several generators round or reinterpret it.

## Generation decisions worth defending in review

- **Level `indep`** (target-independent) with **`opt_level=0`**. MQT Bench's
  target-independent level runs a Qiskit `transpile` internally; at level 0 that is
  a basis translation only. Any higher level would bake Qiskit's optimiser into the
  corpus and quietly hand Qiskit an advantage in a cross-toolchain comparison.
- **Seeded.** `seed=42` where the generator accepts one, and MQT Bench itself pins
  `default_rng(10)` for parameter binding and `seed_transpiler=10`. The `seeded`
  column records which circuits this applied to.
- **Nothing hand-picked.** The whole catalogue is generated; selection is expressed
  as a `selection_tier` column, not by deleting files.
- **Size ladder** 2–32 qubits, with per-algorithm caps (see `provenance.json`) where
  construction blows up combinatorially. Every skipped attempt is logged with its
  reason in `generation_log.csv`, including arity constraints (e.g. the adders need
  even widths, the Steane code a multiple of 13).
- **One documented exception:** `shor_alg_n018` is emitted at *algorithmic* level —
  its target-independent transpilation exceeded a 240 s budget. Shor exists only at
  widths 18, 42, 58, 74. The `level` column marks it.

## Tiers

`selection_tier` — what to run:

| Tier | Count | Meaning |
|---|---|---|
| `CORE` | 190 | 16-algorithm subset spanning every stress class. The headline comparison. |
| `EXTENDED` | 162 | The rest of the catalogue, for robustness checks. |

`portability_tier` — what each toolchain can actually ingest:

| Tier | Count | Meaning |
|---|---|---|
| `A` | 157 | OpenQASM 2 using only the original `qelib1.inc` gate set. Safe everywhere, including Bloqade. |
| `A-EXT` | 152 | OpenQASM 2, but uses Qiskit extensions outside strict `qelib1` (`cp`, `rxx`, `rzz`, `p`, `sx`, `cu`, `c3sqrtx`, `rccx`, …). May need pre-translation for Cirq/Bloqade. |
| `B` | 43 | OpenQASM 3 only — dynamic control flow, no QASM 2 export exists. Affects `ae`, `iqpe`, `dynamic_qft`, `ghz_dynamic`. |

**Tier A is the fair cross-toolchain comparison set.** A/A-EXT/B coverage per
toolchain is itself a reportable result: the fraction of a standard corpus each
toolchain can even express.

`stress_class` — which part of a pipeline the circuit exercises: `entangling-structure`,
`routing-stress`, `canonical-dense`, `canonical-composite`, `oracle-shallow`,
`oracle-decomposition`, `variational`, `arithmetic-synthesis`, `fault-tolerant`,
`dynamic-control`, `unstructured-control`, `industry-workload`, `depth-stress`.

## QA

Every OpenQASM 2 file was re-parsed with Qiskit's strict parser: **309/309 round-trip,
0 failures**, qubit counts match the manifest. Per-file flags: `strict_qelib1`,
`non_qelib1_gates`, `has_barrier`, `has_custom_gate_defs`, `has_opaque`,
`has_classical_conditional`. Truncated SHA-256 of each file is in the manifest so
drift is detectable.

## Loading

```python
# Qiskit
from qiskit import qasm2
qc = qasm2.load(path, custom_instructions=qasm2.LEGACY_CUSTOM_INSTRUCTIONS,
                custom_classical=qasm2.LEGACY_CUSTOM_CLASSICAL)

# Cirq
from cirq.contrib.qasm_import import circuit_from_qasm
c = circuit_from_qasm(open(path).read())

# PennyLane
import pennylane as qml
tape = qml.from_qasm(open(path).read())

# BQSKit
from bqskit import Circuit
c = Circuit.from_file(path)

# Kirin / Bloqade  (QASM 2 only — prefer portability_tier == "A")
from bloqade import qasm2 as bq
```

Note the `LEGACY_CUSTOM_INSTRUCTIONS` argument: Qiskit's own QASM 2 output is not
loadable by Qiskit's own strict parser without it. That is a finding, not a
workaround — it is exactly why `strict_qelib1` is a manifest column.

## Known gaps

- `iqpe` collapses to a single 2-qubit instance regardless of requested size.
- `shor` at 42+ qubits, `qwalk` above 6 and `grover` above 10 were not generated
  within budget; all are logged.
- Timing columns (`gen_seconds`) are host-specific and are provenance, not results.

## Licence

Circuits are generated output of MQT Bench (MIT). Verify and restate the upstream
licence before redistribution, and cite the MQT Bench paper alongside this corpus.
