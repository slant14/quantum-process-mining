OPENQASM 3.0;
include "stdgates.inc";
gate rxx(p0) _gate_q_0, _gate_q_1 {
  h _gate_q_0;
  h _gate_q_1;
  cx _gate_q_0, _gate_q_1;
  rz(p0) _gate_q_1;
  cx _gate_q_0, _gate_q_1;
  h _gate_q_1;
  h _gate_q_0;
}
gate csdg _gate_q_0, _gate_q_1 {
  tdg _gate_q_0;
  cx _gate_q_0, _gate_q_1;
  t _gate_q_1;
  cx _gate_q_0, _gate_q_1;
  tdg _gate_q_1;
}
bit[2] meas;
qubit[2] q;
rxx(3.2220464314480877) q[0], q[1];
crx(2.6735518805676657) q[1], q[0];
csdg q[0], q[1];
p(5.196847304624584) q[0];
y q[1];
barrier q[0], q[1];
meas[0] = measure q[0];
meas[1] = measure q[1];
