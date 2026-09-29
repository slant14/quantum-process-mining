OPENQASM 3.0;
include "stdgates.inc";
bit[6] bsm0;
bit[2] psm0;
bit[1] m0;
bit[6] bsm1;
bit[2] psm1;
bit[1] m1;
qubit[9] q0;
qubit[6] bs0;
qubit[2] ps0;
qubit[9] q1;
qubit[6] bs1;
qubit[2] ps1;
cx q0[0], q0[3];
h q0[3];
cx q0[3], q0[4];
cx q0[3], q0[5];
cx q0[0], q0[6];
h q0[0];
cx q0[0], q0[1];
cx q0[0], q0[2];
h q0[6];
cx q0[6], q0[7];
cx q0[6], q0[8];
barrier q0[0], q0[1], q0[2], q0[3], q0[4], q0[5], q0[6], q0[7], q0[8], bs0[0], bs0[1], bs0[2], bs0[3], bs0[4], bs0[5], ps0[0], ps0[1];
cx q0[0], bs0[0];
cx q0[1], bs0[1];
cx q0[2], bs0[0];
cx q0[2], bs0[1];
cx q0[3], bs0[2];
cx q0[4], bs0[3];
cx q0[5], bs0[2];
cx q0[5], bs0[3];
cx q0[6], bs0[4];
cx q0[7], bs0[5];
cx q0[8], bs0[4];
cx q0[8], bs0[5];
barrier q0[0], q0[1], q0[2], q0[3], q0[4], q0[5], q0[6], q0[7], q0[8], bs0[0], bs0[1], bs0[2], bs0[3], bs0[4], bs0[5], ps0[0], ps0[1];
h ps0[0];
cx ps0[0], q0[0];
cx ps0[0], q0[1];
cx ps0[0], q0[2];
cx ps0[0], q0[6];
cx ps0[0], q0[7];
cx ps0[0], q0[8];
h ps0[0];
h ps0[1];
cx ps0[1], q0[3];
cx ps0[1], q0[4];
cx ps0[1], q0[5];
cx ps0[1], q0[6];
cx ps0[1], q0[7];
cx ps0[1], q0[8];
h ps0[1];
barrier q0[0], q0[1], q0[2], q0[3], q0[4], q0[5], q0[6], q0[7], q0[8], bs0[0], bs0[1], bs0[2], bs0[3], bs0[4], bs0[5], ps0[0], ps0[1];
cx q1[0], q1[3];
h q1[3];
cx q1[3], q1[4];
cx q1[3], q1[5];
cx q1[0], q1[6];
h q1[0];
cx q1[0], q1[1];
cx q1[0], q1[2];
h q1[6];
cx q1[6], q1[7];
cx q1[6], q1[8];
barrier q1[0], q1[1], q1[2], q1[3], q1[4], q1[5], q1[6], q1[7], q1[8], bs1[0], bs1[1], bs1[2], bs1[3], bs1[4], bs1[5], ps1[0], ps1[1];
cx q1[0], bs1[0];
cx q1[1], bs1[1];
cx q1[2], bs1[0];
cx q1[2], bs1[1];
cx q1[3], bs1[2];
cx q1[4], bs1[3];
cx q1[5], bs1[2];
cx q1[5], bs1[3];
cx q1[6], bs1[4];
cx q1[7], bs1[5];
cx q1[8], bs1[4];
cx q1[8], bs1[5];
barrier q1[0], q1[1], q1[2], q1[3], q1[4], q1[5], q1[6], q1[7], q1[8], bs1[0], bs1[1], bs1[2], bs1[3], bs1[4], bs1[5], ps1[0], ps1[1];
h ps1[0];
cx ps1[0], q1[0];
cx ps1[0], q1[1];
cx ps1[0], q1[2];
cx ps1[0], q1[6];
cx ps1[0], q1[7];
cx ps1[0], q1[8];
h ps1[0];
h ps1[1];
cx ps1[1], q1[3];
cx ps1[1], q1[4];
cx ps1[1], q1[5];
cx ps1[1], q1[6];
cx ps1[1], q1[7];
cx ps1[1], q1[8];
h ps1[1];
barrier q1[0], q1[1], q1[2], q1[3], q1[4], q1[5], q1[6], q1[7], q1[8], bs1[0], bs1[1], bs1[2], bs1[3], bs1[4], bs1[5], ps1[0], ps1[1];
bsm0[0] = measure bs0[0];
bsm0[1] = measure bs0[1];
bsm0[2] = measure bs0[2];
bsm0[3] = measure bs0[3];
bsm0[4] = measure bs0[4];
bsm0[5] = measure bs0[5];
if (bsm0 == 1) {
  x q0[0];
}
if (bsm0 == 2) {
  x q0[1];
}
if (bsm0 == 3) {
  x q0[2];
}
if (bsm0 == 4) {
  x q0[3];
}
if (bsm0 == 8) {
  x q0[4];
}
if (bsm0 == 12) {
  x q0[5];
}
if (bsm0 == 16) {
  x q0[6];
}
if (bsm0 == 32) {
  x q0[7];
}
if (bsm0 == 48) {
  x q0[8];
}
barrier q0[0], q0[1], q0[2], q0[3], q0[4], q0[5], q0[6], q0[7], q0[8], bs0[0], bs0[1], bs0[2], bs0[3], bs0[4], bs0[5], ps0[0], ps0[1];
psm0[0] = measure ps0[0];
psm0[1] = measure ps0[1];
if (psm0 == 1) {
  z q0[0];
}
if (psm0 == 2) {
  z q0[3];
}
if (psm0 == 3) {
  z q0[6];
}
barrier q0[0], q0[1], q0[2], q0[3], q0[4], q0[5], q0[6], q0[7], q0[8], bs0[0], bs0[1], bs0[2], bs0[3], bs0[4], bs0[5], ps0[0], ps0[1];
cx q0[0], q0[1];
cx q0[0], q0[2];
h q0[0];
cx q0[3], q0[4];
cx q0[3], q0[5];
h q0[3];
cx q0[0], q0[3];
cx q0[6], q0[7];
cx q0[6], q0[8];
h q0[6];
cx q0[0], q0[6];
m0[0] = measure q0[0];
bsm1[0] = measure bs1[0];
bsm1[1] = measure bs1[1];
bsm1[2] = measure bs1[2];
bsm1[3] = measure bs1[3];
bsm1[4] = measure bs1[4];
bsm1[5] = measure bs1[5];
if (bsm1 == 1) {
  x q1[0];
}
if (bsm1 == 2) {
  x q1[1];
}
if (bsm1 == 3) {
  x q1[2];
}
if (bsm1 == 4) {
  x q1[3];
}
if (bsm1 == 8) {
  x q1[4];
}
if (bsm1 == 12) {
  x q1[5];
}
if (bsm1 == 16) {
  x q1[6];
}
if (bsm1 == 32) {
  x q1[7];
}
if (bsm1 == 48) {
  x q1[8];
}
barrier q1[0], q1[1], q1[2], q1[3], q1[4], q1[5], q1[6], q1[7], q1[8], bs1[0], bs1[1], bs1[2], bs1[3], bs1[4], bs1[5], ps1[0], ps1[1];
psm1[0] = measure ps1[0];
psm1[1] = measure ps1[1];
if (psm1 == 1) {
  z q1[0];
}
if (psm1 == 2) {
  z q1[3];
}
if (psm1 == 3) {
  z q1[6];
}
barrier q1[0], q1[1], q1[2], q1[3], q1[4], q1[5], q1[6], q1[7], q1[8], bs1[0], bs1[1], bs1[2], bs1[3], bs1[4], bs1[5], ps1[0], ps1[1];
cx q1[0], q1[1];
cx q1[0], q1[2];
h q1[0];
cx q1[3], q1[4];
cx q1[3], q1[5];
h q1[3];
cx q1[0], q1[3];
cx q1[6], q1[7];
cx q1[6], q1[8];
h q1[6];
cx q1[0], q1[6];
m1[0] = measure q1[0];
barrier q0[0], q0[1], q0[2], q0[3], q0[4], q0[5], q0[6], q0[7], q0[8], bs0[0], bs0[1], bs0[2], bs0[3], bs0[4], bs0[5], ps0[0], ps0[1], q1[0], q1[1], q1[2], q1[3], q1[4], q1[5], q1[6], q1[7], q1[8], bs1[0], bs1[1], bs1[2], bs1[3], bs1[4], bs1[5], ps1[0], ps1[1];
