OPENQASM 3.0;
include "stdgates.inc";
bit[8] final_measurement;
bit[4] mid_measurement;
qubit[8] q;
h q[0];
cx q[0], q[1];
h q[2];
cx q[2], q[1];
cx q[2], q[3];
h q[4];
cx q[4], q[3];
cx q[4], q[5];
h q[6];
cx q[6], q[5];
mid_measurement[0] = measure q[1];
if (mid_measurement[0]) {
  x q[1];
}
cx q[0], q[1];
final_measurement[0] = measure q[0];
final_measurement[1] = measure q[1];
if (mid_measurement[0] == true) {
  x q[2];
}
mid_measurement[1] = measure q[3];
if (mid_measurement[1]) {
  x q[3];
}
cx q[2], q[3];
final_measurement[2] = measure q[2];
final_measurement[3] = measure q[3];
if ((mid_measurement[0] ^ mid_measurement[1]) == true) {
  x q[4];
}
mid_measurement[2] = measure q[5];
if (mid_measurement[2]) {
  x q[5];
}
cx q[4], q[5];
final_measurement[4] = measure q[4];
final_measurement[5] = measure q[5];
if ((mid_measurement[0] ^ mid_measurement[1] ^ mid_measurement[2]) == true) {
  x q[6];
}
mid_measurement[3] = measure q[7];
if (mid_measurement[3]) {
  x q[7];
}
cx q[6], q[7];
final_measurement[6] = measure q[6];
final_measurement[7] = measure q[7];
