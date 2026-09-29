OPENQASM 3.0;
include "stdgates.inc";
gate MAJ _gate_q_0, _gate_q_1, _gate_q_2 {
  cx _gate_q_0, _gate_q_1;
  cx _gate_q_0, _gate_q_2;
  ccx _gate_q_2, _gate_q_1, _gate_q_0;
}
gate UMA _gate_q_0, _gate_q_1, _gate_q_2 {
  ccx _gate_q_2, _gate_q_1, _gate_q_0;
  cx _gate_q_0, _gate_q_2;
  cx _gate_q_2, _gate_q_1;
}
bit[4] meas;
qubit[1] cin;
qubit[1] a;
qubit[1] b;
qubit[1] cout;
MAJ a[0], b[0], cin[0];
cx a[0], cout[0];
UMA a[0], b[0], cin[0];
barrier cin[0], a[0], b[0], cout[0];
meas[0] = measure cin[0];
meas[1] = measure a[0];
meas[2] = measure b[0];
meas[3] = measure cout[0];
