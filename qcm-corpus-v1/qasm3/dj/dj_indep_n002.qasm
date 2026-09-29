OPENQASM 3.0;
include "stdgates.inc";
gate Oracle _gate_q_0, _gate_q_1 {
  x _gate_q_0;
  cx _gate_q_0, _gate_q_1;
  x _gate_q_0;
}
bit[1] c;
qubit[2] q;
h q[0];
x q[1];
h q[1];
Oracle q[0], q[1];
h q[0];
barrier q[0], q[1];
c[0] = measure q[0];
