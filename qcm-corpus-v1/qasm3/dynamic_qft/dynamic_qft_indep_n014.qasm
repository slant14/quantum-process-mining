OPENQASM 3.0;
include "stdgates.inc";
bit[14] meas;
qubit[14] q;
h q[13];
meas[0] = measure q[13];
if (meas[0]) {
  p(pi/2) q[12];
}
if (meas[0]) {
  p(pi/4) q[11];
}
if (meas[0]) {
  p(pi/8) q[10];
}
if (meas[0]) {
  p(pi/16) q[9];
}
if (meas[0]) {
  p(pi/32) q[8];
}
if (meas[0]) {
  p(pi/64) q[7];
}
if (meas[0]) {
  p(0.02454369260617026) q[6];
}
if (meas[0]) {
  p(0.01227184630308513) q[5];
}
if (meas[0]) {
  p(0.006135923151542565) q[4];
}
if (meas[0]) {
  p(0.0030679615757712823) q[3];
}
if (meas[0]) {
  p(0.0015339807878856412) q[2];
}
if (meas[0]) {
  p(0.0007669903939428206) q[1];
}
if (meas[0]) {
  p(0.0003834951969714103) q[0];
}
h q[12];
meas[1] = measure q[12];
if (meas[1]) {
  p(pi/2) q[11];
}
if (meas[1]) {
  p(pi/4) q[10];
}
if (meas[1]) {
  p(pi/8) q[9];
}
if (meas[1]) {
  p(pi/16) q[8];
}
if (meas[1]) {
  p(pi/32) q[7];
}
if (meas[1]) {
  p(pi/64) q[6];
}
if (meas[1]) {
  p(0.02454369260617026) q[5];
}
if (meas[1]) {
  p(0.01227184630308513) q[4];
}
if (meas[1]) {
  p(0.006135923151542565) q[3];
}
if (meas[1]) {
  p(0.0030679615757712823) q[2];
}
if (meas[1]) {
  p(0.0015339807878856412) q[1];
}
if (meas[1]) {
  p(0.0007669903939428206) q[0];
}
h q[11];
meas[2] = measure q[11];
if (meas[2]) {
  p(pi/2) q[10];
}
if (meas[2]) {
  p(pi/4) q[9];
}
if (meas[2]) {
  p(pi/8) q[8];
}
if (meas[2]) {
  p(pi/16) q[7];
}
if (meas[2]) {
  p(pi/32) q[6];
}
if (meas[2]) {
  p(pi/64) q[5];
}
if (meas[2]) {
  p(0.02454369260617026) q[4];
}
if (meas[2]) {
  p(0.01227184630308513) q[3];
}
if (meas[2]) {
  p(0.006135923151542565) q[2];
}
if (meas[2]) {
  p(0.0030679615757712823) q[1];
}
if (meas[2]) {
  p(0.0015339807878856412) q[0];
}
h q[10];
meas[3] = measure q[10];
if (meas[3]) {
  p(pi/2) q[9];
}
if (meas[3]) {
  p(pi/4) q[8];
}
if (meas[3]) {
  p(pi/8) q[7];
}
if (meas[3]) {
  p(pi/16) q[6];
}
if (meas[3]) {
  p(pi/32) q[5];
}
if (meas[3]) {
  p(pi/64) q[4];
}
if (meas[3]) {
  p(0.02454369260617026) q[3];
}
if (meas[3]) {
  p(0.01227184630308513) q[2];
}
if (meas[3]) {
  p(0.006135923151542565) q[1];
}
if (meas[3]) {
  p(0.0030679615757712823) q[0];
}
h q[9];
meas[4] = measure q[9];
if (meas[4]) {
  p(pi/2) q[8];
}
if (meas[4]) {
  p(pi/4) q[7];
}
if (meas[4]) {
  p(pi/8) q[6];
}
if (meas[4]) {
  p(pi/16) q[5];
}
if (meas[4]) {
  p(pi/32) q[4];
}
if (meas[4]) {
  p(pi/64) q[3];
}
if (meas[4]) {
  p(0.02454369260617026) q[2];
}
if (meas[4]) {
  p(0.01227184630308513) q[1];
}
if (meas[4]) {
  p(0.006135923151542565) q[0];
}
h q[8];
meas[5] = measure q[8];
if (meas[5]) {
  p(pi/2) q[7];
}
if (meas[5]) {
  p(pi/4) q[6];
}
if (meas[5]) {
  p(pi/8) q[5];
}
if (meas[5]) {
  p(pi/16) q[4];
}
if (meas[5]) {
  p(pi/32) q[3];
}
if (meas[5]) {
  p(pi/64) q[2];
}
if (meas[5]) {
  p(0.02454369260617026) q[1];
}
if (meas[5]) {
  p(0.01227184630308513) q[0];
}
h q[7];
meas[6] = measure q[7];
if (meas[6]) {
  p(pi/2) q[6];
}
if (meas[6]) {
  p(pi/4) q[5];
}
if (meas[6]) {
  p(pi/8) q[4];
}
if (meas[6]) {
  p(pi/16) q[3];
}
if (meas[6]) {
  p(pi/32) q[2];
}
if (meas[6]) {
  p(pi/64) q[1];
}
if (meas[6]) {
  p(0.02454369260617026) q[0];
}
h q[6];
meas[7] = measure q[6];
if (meas[7]) {
  p(pi/2) q[5];
}
if (meas[7]) {
  p(pi/4) q[4];
}
if (meas[7]) {
  p(pi/8) q[3];
}
if (meas[7]) {
  p(pi/16) q[2];
}
if (meas[7]) {
  p(pi/32) q[1];
}
if (meas[7]) {
  p(pi/64) q[0];
}
h q[5];
meas[8] = measure q[5];
if (meas[8]) {
  p(pi/2) q[4];
}
if (meas[8]) {
  p(pi/4) q[3];
}
if (meas[8]) {
  p(pi/8) q[2];
}
if (meas[8]) {
  p(pi/16) q[1];
}
if (meas[8]) {
  p(pi/32) q[0];
}
h q[4];
meas[9] = measure q[4];
if (meas[9]) {
  p(pi/2) q[3];
}
if (meas[9]) {
  p(pi/4) q[2];
}
if (meas[9]) {
  p(pi/8) q[1];
}
if (meas[9]) {
  p(pi/16) q[0];
}
h q[3];
meas[10] = measure q[3];
if (meas[10]) {
  p(pi/2) q[2];
}
if (meas[10]) {
  p(pi/4) q[1];
}
if (meas[10]) {
  p(pi/8) q[0];
}
h q[2];
meas[11] = measure q[2];
if (meas[11]) {
  p(pi/2) q[1];
}
if (meas[11]) {
  p(pi/4) q[0];
}
h q[1];
meas[12] = measure q[1];
if (meas[12]) {
  p(pi/2) q[0];
}
h q[0];
meas[13] = measure q[0];
