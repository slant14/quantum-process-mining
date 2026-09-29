OPENQASM 3.0;
include "stdgates.inc";
bit[3] final_measurement;
bit[1] mid_measurement;
qubit[3] q;
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
final_measurement[2] = measure q[2];
