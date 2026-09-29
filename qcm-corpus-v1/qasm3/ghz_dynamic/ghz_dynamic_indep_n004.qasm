OPENQASM 3.0;
include "stdgates.inc";
bit[4] final_measurement;
bit[2] mid_measurement;
qubit[4] q;
h q[0];
cx q[0], q[1];
h q[2];
cx q[2], q[1];
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
