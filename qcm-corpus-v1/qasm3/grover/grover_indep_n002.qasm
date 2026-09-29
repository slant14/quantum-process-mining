OPENQASM 3.0;
include "stdgates.inc";
gate mcphase(_gate_p_0) _gate_q_0, _gate_q_1 {
  cp(pi) _gate_q_0, _gate_q_1;
}
gate Q _gate_q_0, _gate_q_1 {
  mcphase(pi) _gate_q_0, _gate_q_1;
  h _gate_q_0;
  x _gate_q_0;
  z _gate_q_0;
  x _gate_q_0;
  h _gate_q_0;
}
bit[2] meas;
qubit[1] q;
qubit[1] flag;
h q[0];
x flag[0];
Q q[0], flag[0];
barrier q[0], flag[0];
meas[0] = measure q[0];
meas[1] = measure flag[0];
