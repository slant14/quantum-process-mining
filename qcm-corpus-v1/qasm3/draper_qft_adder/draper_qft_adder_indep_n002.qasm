OPENQASM 3.0;
include "stdgates.inc";
gate _circuit_42_1089 _gate_q_0 {
  h _gate_q_0;
}
gate _circuit_42_1089_dg _gate_q_0 {
  h _gate_q_0;
}
bit[2] meas;
qubit[1] a;
qubit[1] b;
_circuit_42_1089 b[0];
cp(pi) a[0], b[0];
_circuit_42_1089_dg b[0];
barrier a[0], b[0];
meas[0] = measure a[0];
meas[1] = measure b[0];
