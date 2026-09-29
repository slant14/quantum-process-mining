"""Second pass: benchmarks whose valid widths are not on the standard ladder."""
import json, time
from build_corpus import generate, STATE

EXTRA = {
    "shor": [18],                       # only 18, 42, 58, 74 exist; 18 is affordable
    "seven_qubit_steane_code": [13, 26],  # width must be a multiple of 13
    "shors_nine_qubit_code": [17, 34],    # width must be a multiple of 17
    "iqpe": [2, 4, 6, 8],
}
done = {(json.loads(l)["algorithm"], json.loads(l)["requested_size"])
        for l in open(STATE) if l.strip()}
with open(STATE, "a") as fh:
    for name, sizes in EXTRA.items():
        for size in sizes:
            if (name, size) in done:
                continue
            r = generate(name, size)
            rec = {"algorithm": name, "requested_size": size, "secs": r["secs"]}
            if r["ok"]:
                rec.update({k: r[k] for k in ("seeded","num_qubits","num_clbits",
                    "depth","size","two_qubit_gates","multi_qubit_gates","ops",
                    "qasm2","qasm3","qasm2_err","qasm3_err")})
                rec["ok"] = True
                print(f"OK   {name}_n{r['num_qubits']:03d} depth={r['depth']} {r['secs']:.1f}s")
            else:
                rec.update({"ok": False, "error": r.get("error","?")})
                print(f"SKIP {name}_{size}: {r.get('error','')[:70]}")
            fh.write(json.dumps(rec) + "\n"); fh.flush()
