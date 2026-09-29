import json, time, resource, hashlib
resource.setrlimit(resource.RLIMIT_AS,(2_800_000_000,)*2)
from mqt.bench import get_benchmark, BenchmarkLevel
from qiskit import qasm2, qasm3
from build_corpus import STATE
t=time.time(); qc=get_benchmark("shor", BenchmarkLevel.ALG, 18)
rec={"algorithm":"shor","requested_size":18,"ok":True,"level":"alg","seeded":False,
     "num_qubits":qc.num_qubits,"num_clbits":qc.num_clbits,"depth":qc.depth(),
     "size":qc.size(),
     "two_qubit_gates":sum(1 for i in qc.data if len(i.qubits)==2),
     "multi_qubit_gates":sum(1 for i in qc.data if len(i.qubits)>2),
     "ops":{k:int(v) for k,v in qc.count_ops().items()},
     "qasm2":qasm2.dumps(qc),"qasm3":qasm3.dumps(qc),
     "qasm2_err":"","qasm3_err":"","secs":round(time.time()-t,3)}
lines=[l for l in open(STATE) if l.strip() and json.loads(l)["algorithm"]!="shor"]
lines.append(json.dumps(rec)+"\n"); open(STATE,"w").writelines(lines)
print("added shor n=18 level=alg depth=",qc.depth())
