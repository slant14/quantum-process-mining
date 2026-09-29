OPENQASM 3.0;
include "stdgates.inc";
bit[5] meas;
qubit[5] q;
h q[4];
meas[0] = measure q[4];
if (meas[0]) {
  p(pi/2) q[3];
}
if (meas[0]) {
  p(pi/4) q[2];
}
if (meas[0]) {
  p(pi/8) q[1];
}
if (meas[0]) {
  p(pi/16) q[0];
}
h q[3];
meas[1] = measure q[3];
if (meas[1]) {
  p(pi/2) q[2];
}
if (meas[1]) {
  p(pi/4) q[1];
}
if (meas[1]) {
  p(pi/8) q[0];
}
h q[2];
meas[2] = measure q[2];
if (meas[2]) {
  p(pi/2) q[1];
}
if (meas[2]) {
  p(pi/4) q[0];
}
h q[1];
meas[3] = measure q[1];
if (meas[3]) {
  p(pi/2) q[0];
}
h q[0];
meas[4] = measure q[0];
