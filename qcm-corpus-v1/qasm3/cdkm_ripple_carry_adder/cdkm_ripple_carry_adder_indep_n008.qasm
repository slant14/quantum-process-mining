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
bit[8] meas;
qubit[1] cin;
qubit[3] a;
qubit[3] b;
qubit[1] cout;
MAJ a[0], b[0], cin[0];
MAJ a[1], b[1], a[0];
MAJ a[2], b[2], a[1];
cx a[2], cout[0];
UMA a[2], b[2], a[1];
UMA a[1], b[1], a[0];
UMA a[0], b[0], cin[0];
barrier cin[0], a[0], a[1], a[2], b[0], b[1], b[2], cout[0];
meas[0] = measure cin[0];
meas[1] = measure a[0];
meas[2] = measure a[1];
meas[3] = measure a[2];
meas[4] = measure b[0];
meas[5] = measure b[1];
meas[6] = measure b[2];
meas[7] = measure cout[0];
