OPENQASM 3.0;
include "stdgates.inc";
gate c3sx _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3 {
  h _gate_q_3;
  cp(pi/8) _gate_q_0, _gate_q_3;
  h _gate_q_3;
  cx _gate_q_0, _gate_q_1;
  h _gate_q_3;
  cp(-pi/8) _gate_q_1, _gate_q_3;
  h _gate_q_3;
  cx _gate_q_0, _gate_q_1;
  h _gate_q_3;
  cp(pi/8) _gate_q_1, _gate_q_3;
  h _gate_q_3;
  cx _gate_q_1, _gate_q_2;
  h _gate_q_3;
  cp(-pi/8) _gate_q_2, _gate_q_3;
  h _gate_q_3;
  cx _gate_q_0, _gate_q_2;
  h _gate_q_3;
  cp(pi/8) _gate_q_2, _gate_q_3;
  h _gate_q_3;
  cx _gate_q_1, _gate_q_2;
  h _gate_q_3;
  cp(-pi/8) _gate_q_2, _gate_q_3;
  h _gate_q_3;
  cx _gate_q_0, _gate_q_2;
  h _gate_q_3;
  cp(pi/8) _gate_q_2, _gate_q_3;
  h _gate_q_3;
}
gate ecr _gate_q_0, _gate_q_1 {
  s _gate_q_0;
  sx _gate_q_1;
  cx _gate_q_0, _gate_q_1;
  x _gate_q_0;
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
gate rzz(p0) _gate_q_0, _gate_q_1 {
  cx _gate_q_0, _gate_q_1;
  rz(p0) _gate_q_1;
  cx _gate_q_0, _gate_q_1;
}
gate cs _gate_q_0, _gate_q_1 {
  t _gate_q_0;
  cx _gate_q_0, _gate_q_1;
  tdg _gate_q_1;
  cx _gate_q_0, _gate_q_1;
  t _gate_q_1;
}
gate csx _gate_q_0, _gate_q_1 {
  h _gate_q_1;
  cs _gate_q_0, _gate_q_1;
  h _gate_q_1;
}
bit[6] meas;
qubit[6] q;
t q[3];
tdg q[3];
cry(2.125069481984559) q[4], q[1];
cswap q[5], q[2], q[0];
c3sx q[1], q[5], q[2], q[0];
tdg q[1];
cz q[2], q[3];
t q[2];
ecr q[4], q[0];
cry(4.875952527358193) q[5], q[4];
ccx q[2], q[4], q[0];
ccx q[3], q[5], q[1];
rccx q[1], q[0], q[3];
rccx q[4], q[5], q[2];
rccx q[1], q[5], q[0];
ccx q[3], q[2], q[4];
ccx q[0], q[4], q[3];
cy q[1], q[2];
ccz q[1], q[3], q[0];
rzz(3.0727799917118745) q[4], q[2];
ccz q[3], q[1], q[4];
sx q[1];
h q[5];
rccx q[0], q[5], q[2];
ccx q[0], q[3], q[4];
rccx q[1], q[4], q[3];
csx q[5], q[0];
barrier q[0], q[1], q[2], q[3], q[4], q[5];
meas[0] = measure q[0];
meas[1] = measure q[1];
meas[2] = measure q[2];
meas[3] = measure q[3];
meas[4] = measure q[4];
meas[5] = measure q[5];
