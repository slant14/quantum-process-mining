"""QA pass: round-trip every QASM2 file and flag cross-toolchain portability."""
import csv, json, re, collections
from pathlib import Path
from qiskit import qasm2

OUT = Path("/mnt/user-data/outputs/qcm-corpus-v1")

# Gate set of the original qelib1.inc shipped with the OpenQASM 2 spec.
# Anything outside this is a Qiskit extension and may not load elsewhere.
QELIB1 = {"u3","u2","u1","cx","id","u0","x","y","z","h","s","sdg","t","tdg",
          "rx","ry","rz","cz","cy","swap","ch","ccx","crz","cu1","cu3",
          "barrier","measure","reset","qreg","creg"}
DECL = re.compile(r"^\s*(?:gate|opaque)\s+(\w+)", re.M)
CALL = re.compile(r"^\s*([a-zA-Z][\w]*)\s*(?:\(|\s+q)", re.M)

rows = list(csv.DictReader((OUT / "manifest.csv").open()))
extra_counter = collections.Counter()
new = ["roundtrip_ok","roundtrip_qubits_match","strict_qelib1",
       "non_qelib1_gates","has_barrier","has_custom_gate_defs","has_opaque",
       "has_classical_conditional"]

for r in rows:
    if not r["qasm2_path"]:
        for k in new: r[k] = ""
        continue
    txt = (OUT / r["qasm2_path"]).read_text()
    try:
        qc = qasm2.loads(txt,
                         custom_instructions=qasm2.LEGACY_CUSTOM_INSTRUCTIONS,
                         custom_classical=qasm2.LEGACY_CUSTOM_CLASSICAL)
        r["roundtrip_ok"] = "True"
        r["roundtrip_qubits_match"] = str(qc.num_qubits == int(r["num_qubits"]))
    except Exception as e:
        r["roundtrip_ok"] = f"False:{type(e).__name__}"
        r["roundtrip_qubits_match"] = "False"
    locally_defined = set(DECL.findall(txt))
    used = {g for g in CALL.findall(txt)} - {"include","OPENQASM","gate","opaque","if"}
    extra = sorted((used - QELIB1) - locally_defined)
    extra_counter.update(extra)
    r["strict_qelib1"] = str(len(extra) == 0)
    r["non_qelib1_gates"] = ";".join(extra)
    r["has_barrier"] = str("barrier" in txt)
    r["has_custom_gate_defs"] = str(bool(re.search(r"^gate\s", txt, re.M)))
    r["has_opaque"] = str(bool(re.search(r"^opaque\s", txt, re.M)))
    r["has_classical_conditional"] = str("if(" in txt.replace(" ", ""))

with (OUT / "manifest.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

q2 = [r for r in rows if r["qasm2_path"]]
bad = [r["circuit_id"] for r in q2 if r["roundtrip_ok"].startswith("False")]
strict = sum(1 for r in q2 if r["strict_qelib1"] == "True")
print(f"rows={len(rows)} qasm2={len(q2)} roundtrip_fail={len(bad)} {bad[:5]}")
print(f"strict qelib1: {strict}/{len(q2)}")
print("non-qelib1 gates seen:", dict(extra_counter))
