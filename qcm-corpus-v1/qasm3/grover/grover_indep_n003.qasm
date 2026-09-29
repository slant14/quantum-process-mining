OPENQASM 3.0;
include "stdgates.inc";
gate mcphase(_gate_p_0) _gate_q_0, _gate_q_1, _gate_q_2 {
  cx _gate_q_0, _gate_q_2;
  rz(-pi/4) _gate_q_2;
  cx _gate_q_1, _gate_q_2;
  rz(pi/4) _gate_q_2;
  cx _gate_q_0, _gate_q_2;
  rz(-pi/4) _gate_q_2;
  cx _gate_q_1, _gate_q_2;
  rz(pi/4) _gate_q_2;
  crz(pi/2) _gate_q_0, _gate_q_1;
  p(pi/4) _gate_q_0;
}
gate Q _gate_q_0, _gate_q_1, _gate_q_2 {
  mcphase(pi) _gate_q_0, _gate_q_1, _gate_q_2;
  h _gate_q_0;
  h _gate_q_1;
  x _gate_q_0;
  x _gate_q_1;
  h _gate_q_1;
  cx _gate_q_0, _gate_q_1;
  h _gate_q_1;
  x _gate_q_0;
  x _gate_q_1;
  h _gate_q_0;
  h _gate_q_1;
}
bit[3] meas;
qubit[2] q;
qubit[1] flag;
h q[0];
h q[1];
x flag[0];
Q q[0], q[1], flag[0];
barrier q[0], q[1], flag[0];
meas[0] = measure q[0];
meas[1] = measure q[1];
meas[2] = measure flag[0];
