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
qubit[14] q;
MAJ q[1], q[7], q[0];
MAJ q[2], q[8], q[1];
MAJ q[3], q[9], q[2];
MAJ q[4], q[10], q[3];
MAJ q[5], q[11], q[4];
MAJ q[6], q[12], q[5];
cx q[6], q[13];
UMA q[6], q[12], q[5];
UMA q[5], q[11], q[4];
UMA q[4], q[10], q[3];
UMA q[3], q[9], q[2];
UMA q[2], q[8], q[1];
UMA q[1], q[7], q[0];
barrier q[0], q[1], q[2], q[3], q[4], q[5], q[6], q[7], q[8], q[9], q[10], q[11], q[12], q[13];
meas[0] = measure q[0];
meas[1] = measure q[1];
meas[2] = measure q[2];
meas[3] = measure q[3];
meas[4] = measure q[4];
meas[5] = measure q[5];
meas[6] = measure q[6];
meas[7] = measure q[7];
meas[8] = measure q[8];
meas[9] = measure q[9];
meas[10] = measure q[10];
meas[11] = measure q[11];
meas[12] = measure q[12];
meas[13] = measure q[13];
