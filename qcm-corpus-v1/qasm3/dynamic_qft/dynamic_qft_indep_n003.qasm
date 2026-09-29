OPENQASM 3.0;
include "stdgates.inc";
bit[3] meas;
qubit[3] q;
h q[2];
meas[0] = measure q[2];
if (meas[0]) {
  p(pi/2) q[1];
}
if (meas[0]) {
  p(pi/4) q[0];
}
h q[1];
meas[1] = measure q[1];
if (meas[1]) {
  p(pi/2) q[0];
}
h q[0];
meas[2] = measure q[0];
