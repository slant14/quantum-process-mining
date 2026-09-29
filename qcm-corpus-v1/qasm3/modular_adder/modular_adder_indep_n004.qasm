OPENQASM 3.0;
include "stdgates.inc";
gate qft_dg _gate_q_0, _gate_q_1 {
  swap _gate_q_0, _gate_q_1;
  h _gate_q_0;
  cp(-pi/2) _gate_q_1, _gate_q_0;
  h _gate_q_1;
}
bit[4] meas;
qubit[4] q;
h q[3];
cp(pi/2) q[3], q[2];
h q[2];
swap q[2], q[3];
cp(pi) q[0], q[3];
cp(pi/2) q[0], q[2];
cp(pi) q[1], q[2];
qft_dg q[2], q[3];
barrier q[0], q[1], q[2], q[3];
meas[0] = measure q[0];
meas[1] = measure q[1];
meas[2] = measure q[2];
meas[3] = measure q[3];
