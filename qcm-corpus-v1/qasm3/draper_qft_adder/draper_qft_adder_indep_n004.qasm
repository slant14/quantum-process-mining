OPENQASM 3.0;
include "stdgates.inc";
gate _circuit_42_1093 _gate_q_0, _gate_q_1 {
  h _gate_q_1;
  cp(pi/2) _gate_q_1, _gate_q_0;
  h _gate_q_0;
}
gate _circuit_42_1093_dg _gate_q_0, _gate_q_1 {
  h _gate_q_0;
  cp(-pi/2) _gate_q_1, _gate_q_0;
  h _gate_q_1;
}
bit[4] meas;
qubit[2] a;
qubit[2] b;
_circuit_42_1093 b[0], b[1];
cp(pi) a[0], b[0];
cp(pi/2) a[0], b[1];
cp(pi) a[1], b[1];
_circuit_42_1093_dg b[0], b[1];
barrier a[0], a[1], b[0], b[1];
meas[0] = measure a[0];
meas[1] = measure a[1];
meas[2] = measure b[0];
meas[3] = measure b[1];
