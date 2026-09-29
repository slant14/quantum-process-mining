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
qubit[8] q;
MAJ q[1], q[4], q[0];
MAJ q[2], q[5], q[1];
MAJ q[3], q[6], q[2];
cx q[3], q[7];
UMA q[3], q[6], q[2];
UMA q[2], q[5], q[1];
UMA q[1], q[4], q[0];
barrier q[0], q[1], q[2], q[3], q[4], q[5], q[6], q[7];
meas[0] = measure q[0];
meas[1] = measure q[1];
meas[2] = measure q[2];
meas[3] = measure q[3];
meas[4] = measure q[4];
meas[5] = measure q[5];
meas[6] = measure q[6];
meas[7] = measure q[7];
