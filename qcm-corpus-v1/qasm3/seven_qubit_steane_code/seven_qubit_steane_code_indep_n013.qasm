OPENQASM 3.0;
include "stdgates.inc";
bit[3] bfsm0;
bit[3] pfsm0;
bit[1] m0;
qubit[7] q0;
qubit[3] bfs0;
qubit[3] pfs0;
cx q0[0], q0[1];
cx q0[0], q0[2];
h q0[4];
h q0[5];
h q0[6];
cx q0[6], q0[3];
cx q0[5], q0[3];
cx q0[4], q0[3];
cx q0[5], q0[2];
cx q0[4], q0[2];
cx q0[6], q0[1];
cx q0[4], q0[1];
cx q0[6], q0[0];
cx q0[5], q0[0];
barrier q0[0], q0[1], q0[2], q0[3], q0[4], q0[5], q0[6], bfs0[0], bfs0[1], bfs0[2], pfs0[0], pfs0[1], pfs0[2];
cx q0[0], bfs0[0];
cx q0[1], bfs0[1];
cx q0[2], bfs0[0];
cx q0[2], bfs0[1];
cx q0[3], bfs0[2];
cx q0[4], bfs0[0];
cx q0[4], bfs0[2];
cx q0[5], bfs0[1];
cx q0[5], bfs0[2];
cx q0[6], bfs0[0];
cx q0[6], bfs0[1];
cx q0[6], bfs0[2];
h pfs0[0];
cx pfs0[0], q0[0];
cx pfs0[0], q0[2];
cx pfs0[0], q0[4];
cx pfs0[0], q0[6];
h pfs0[0];
h pfs0[1];
cx pfs0[1], q0[1];
cx pfs0[1], q0[2];
cx pfs0[1], q0[5];
cx pfs0[1], q0[6];
h pfs0[1];
h pfs0[2];
cx pfs0[2], q0[3];
cx pfs0[2], q0[4];
cx pfs0[2], q0[5];
cx pfs0[2], q0[6];
h pfs0[2];
barrier q0[0], q0[1], q0[2], q0[3], q0[4], q0[5], q0[6], bfs0[0], bfs0[1], bfs0[2], pfs0[0], pfs0[1], pfs0[2];
bfsm0[0] = measure bfs0[0];
bfsm0[1] = measure bfs0[1];
bfsm0[2] = measure bfs0[2];
if (bfsm0 == 1) {
  x q0[0];
}
if (bfsm0 == 2) {
  x q0[1];
}
if (bfsm0 == 3) {
  x q0[2];
}
if (bfsm0 == 4) {
  x q0[3];
}
if (bfsm0 == 5) {
  x q0[4];
}
if (bfsm0 == 6) {
  x q0[5];
}
if (bfsm0 == 7) {
  x q0[6];
}
pfsm0[0] = measure pfs0[0];
pfsm0[1] = measure pfs0[1];
pfsm0[2] = measure pfs0[2];
if (pfsm0 == 1) {
  z q0[0];
}
if (pfsm0 == 2) {
  z q0[1];
}
if (pfsm0 == 3) {
  z q0[2];
}
if (pfsm0 == 4) {
  z q0[3];
}
if (pfsm0 == 5) {
  z q0[4];
}
if (pfsm0 == 6) {
  z q0[5];
}
if (pfsm0 == 7) {
  z q0[6];
}
barrier q0[0], q0[1], q0[2], q0[3], q0[4], q0[5], q0[6], bfs0[0], bfs0[1], bfs0[2], pfs0[0], pfs0[1], pfs0[2];
cx q0[4], q0[1];
cx q0[4], q0[2];
cx q0[4], q0[3];
h q0[4];
cx q0[5], q0[0];
cx q0[5], q0[2];
cx q0[5], q0[3];
h q0[5];
cx q0[6], q0[0];
cx q0[0], q0[2];
cx q0[6], q0[1];
cx q0[0], q0[1];
cx q0[6], q0[3];
h q0[6];
m0[0] = measure q0[0];
barrier q0[0], q0[1], q0[2], q0[3], q0[4], q0[5], q0[6], bfs0[0], bfs0[1], bfs0[2], pfs0[0], pfs0[1], pfs0[2];
