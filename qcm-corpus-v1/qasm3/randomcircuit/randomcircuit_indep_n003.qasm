OPENQASM 3.0;
include "stdgates.inc";
gate cu1(p0) _gate_q_0, _gate_q_1 {
  p(0.5*p0) _gate_q_0;
  cx _gate_q_0, _gate_q_1;
  p((-0.5)*p0) _gate_q_1;
  cx _gate_q_0, _gate_q_1;
  p(0.5*p0) _gate_q_1;
}
gate rccx _gate_q_0, _gate_q_1, _gate_q_2 {
  h _gate_q_2;
  t _gate_q_2;
  cx _gate_q_1, _gate_q_2;
  tdg _gate_q_2;
  cx _gate_q_0, _gate_q_2;
  t _gate_q_2;
  cx _gate_q_1, _gate_q_2;
  tdg _gate_q_2;
  h _gate_q_2;
}
gate ccz _gate_q_0, _gate_q_1, _gate_q_2 {
  h _gate_q_2;
  ccx _gate_q_0, _gate_q_1, _gate_q_2;
  h _gate_q_2;
}
gate sxdg _gate_q_0 {
  s _gate_q_0;
  h _gate_q_0;
  s _gate_q_0;
}
bit[3] meas;
qubit[3] q;
t q[0];
cu1(5.288856933750764) q[1], q[2];
rccx q[1], q[2], q[0];
ccz q[2], q[0], q[1];
sxdg q[0];
cu1(2.026167409578137) q[1], q[0];
cswap q[1], q[2], q[0];
barrier q[0], q[1], q[2];
meas[0] = measure q[0];
meas[1] = measure q[1];
meas[2] = measure q[2];
