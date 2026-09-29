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
bit[14] meas;
qubit[1] cin;
qubit[6] a;
qubit[6] b;
qubit[1] cout;
MAJ a[0], b[0], cin[0];
MAJ a[1], b[1], a[0];
MAJ a[2], b[2], a[1];
MAJ a[3], b[3], a[2];
MAJ a[4], b[4], a[3];
MAJ a[5], b[5], a[4];
cx a[5], cout[0];
UMA a[5], b[5], a[4];
UMA a[4], b[4], a[3];
UMA a[3], b[3], a[2];
UMA a[2], b[2], a[1];
UMA a[1], b[1], a[0];
UMA a[0], b[0], cin[0];
barrier cin[0], a[0], a[1], a[2], a[3], a[4], a[5], b[0], b[1], b[2], b[3], b[4], b[5], cout[0];
meas[0] = measure cin[0];
meas[1] = measure a[0];
meas[2] = measure a[1];
meas[3] = measure a[2];
meas[4] = measure a[3];
meas[5] = measure a[4];
meas[6] = measure a[5];
meas[7] = measure b[0];
meas[8] = measure b[1];
meas[9] = measure b[2];
meas[10] = measure b[3];
meas[11] = measure b[4];
meas[12] = measure b[5];
meas[13] = measure cout[0];
