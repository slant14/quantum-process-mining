OPENQASM 3.0;
include "stdgates.inc";
bit[7] meas;
qubit[7] q;
h q[6];
meas[0] = measure q[6];
if (meas[0]) {
  p(pi/2) q[5];
}
if (meas[0]) {
  p(pi/4) q[4];
}
if (meas[0]) {
  p(pi/8) q[3];
}
if (meas[0]) {
  p(pi/16) q[2];
}
if (meas[0]) {
  p(pi/32) q[1];
}
if (meas[0]) {
  p(pi/64) q[0];
}
h q[5];
meas[1] = measure q[5];
if (meas[1]) {
  p(pi/2) q[4];
}
if (meas[1]) {
  p(pi/4) q[3];
}
if (meas[1]) {
  p(pi/8) q[2];
}
if (meas[1]) {
  p(pi/16) q[1];
}
if (meas[1]) {
  p(pi/32) q[0];
}
h q[4];
meas[2] = measure q[4];
if (meas[2]) {
  p(pi/2) q[3];
}
if (meas[2]) {
  p(pi/4) q[2];
}
if (meas[2]) {
  p(pi/8) q[1];
}
if (meas[2]) {
  p(pi/16) q[0];
}
h q[3];
meas[3] = measure q[3];
if (meas[3]) {
  p(pi/2) q[2];
}
if (meas[3]) {
  p(pi/4) q[1];
}
if (meas[3]) {
  p(pi/8) q[0];
}
h q[2];
meas[4] = measure q[2];
if (meas[4]) {
  p(pi/2) q[1];
}
if (meas[4]) {
  p(pi/4) q[0];
}
h q[1];
meas[5] = measure q[1];
if (meas[5]) {
  p(pi/2) q[0];
}
h q[0];
meas[6] = measure q[0];
