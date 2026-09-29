OPENQASM 3.0;
include "stdgates.inc";
bit[32] final_measurement;
bit[16] mid_measurement;
qubit[32] q;
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
cx q[6], q[7];
h q[8];
cx q[8], q[7];
cx q[8], q[9];
h q[10];
cx q[10], q[9];
cx q[10], q[11];
h q[12];
cx q[12], q[11];
cx q[12], q[13];
h q[14];
cx q[14], q[13];
cx q[14], q[15];
h q[16];
cx q[16], q[15];
cx q[16], q[17];
h q[18];
cx q[18], q[17];
cx q[18], q[19];
h q[20];
cx q[20], q[19];
cx q[20], q[21];
h q[22];
cx q[22], q[21];
cx q[22], q[23];
h q[24];
cx q[24], q[23];
cx q[24], q[25];
h q[26];
cx q[26], q[25];
cx q[26], q[27];
h q[28];
cx q[28], q[27];
cx q[28], q[29];
h q[30];
cx q[30], q[29];
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
if ((mid_measurement[0] ^ mid_measurement[1] ^ mid_measurement[2] ^ mid_measurement[3]) == true) {
  x q[8];
}
mid_measurement[4] = measure q[9];
if (mid_measurement[4]) {
  x q[9];
}
cx q[8], q[9];
final_measurement[8] = measure q[8];
final_measurement[9] = measure q[9];
if ((mid_measurement[0] ^ mid_measurement[1] ^ mid_measurement[2] ^ mid_measurement[3] ^ mid_measurement[4]) == true) {
  x q[10];
}
mid_measurement[5] = measure q[11];
if (mid_measurement[5]) {
  x q[11];
}
cx q[10], q[11];
final_measurement[10] = measure q[10];
final_measurement[11] = measure q[11];
if ((mid_measurement[0] ^ mid_measurement[1] ^ mid_measurement[2] ^ mid_measurement[3] ^ mid_measurement[4] ^ mid_measurement[5]) == true) {
  x q[12];
}
mid_measurement[6] = measure q[13];
if (mid_measurement[6]) {
  x q[13];
}
cx q[12], q[13];
final_measurement[12] = measure q[12];
final_measurement[13] = measure q[13];
if ((mid_measurement[0] ^ mid_measurement[1] ^ mid_measurement[2] ^ mid_measurement[3] ^ mid_measurement[4] ^ mid_measurement[5] ^ mid_measurement[6]) == true) {
  x q[14];
}
mid_measurement[7] = measure q[15];
if (mid_measurement[7]) {
  x q[15];
}
cx q[14], q[15];
final_measurement[14] = measure q[14];
final_measurement[15] = measure q[15];
if ((mid_measurement[0] ^ mid_measurement[1] ^ mid_measurement[2] ^ mid_measurement[3] ^ mid_measurement[4] ^ mid_measurement[5] ^ mid_measurement[6] ^ mid_measurement[7]) == true) {
  x q[16];
}
mid_measurement[8] = measure q[17];
if (mid_measurement[8]) {
  x q[17];
}
cx q[16], q[17];
final_measurement[16] = measure q[16];
final_measurement[17] = measure q[17];
if ((mid_measurement[0] ^ mid_measurement[1] ^ mid_measurement[2] ^ mid_measurement[3] ^ mid_measurement[4] ^ mid_measurement[5] ^ mid_measurement[6] ^ mid_measurement[7] ^ mid_measurement[8]) == true) {
  x q[18];
}
mid_measurement[9] = measure q[19];
if (mid_measurement[9]) {
  x q[19];
}
cx q[18], q[19];
final_measurement[18] = measure q[18];
final_measurement[19] = measure q[19];
if ((mid_measurement[0] ^ mid_measurement[1] ^ mid_measurement[2] ^ mid_measurement[3] ^ mid_measurement[4] ^ mid_measurement[5] ^ mid_measurement[6] ^ mid_measurement[7] ^ mid_measurement[8] ^ mid_measurement[9]) == true) {
  x q[20];
}
mid_measurement[10] = measure q[21];
if (mid_measurement[10]) {
  x q[21];
}
cx q[20], q[21];
final_measurement[20] = measure q[20];
final_measurement[21] = measure q[21];
if ((mid_measurement[0] ^ mid_measurement[1] ^ mid_measurement[2] ^ mid_measurement[3] ^ mid_measurement[4] ^ mid_measurement[5] ^ mid_measurement[6] ^ mid_measurement[7] ^ mid_measurement[8] ^ mid_measurement[9] ^ mid_measurement[10]) == true) {
  x q[22];
}
mid_measurement[11] = measure q[23];
if (mid_measurement[11]) {
  x q[23];
}
cx q[22], q[23];
final_measurement[22] = measure q[22];
final_measurement[23] = measure q[23];
if ((mid_measurement[0] ^ mid_measurement[1] ^ mid_measurement[2] ^ mid_measurement[3] ^ mid_measurement[4] ^ mid_measurement[5] ^ mid_measurement[6] ^ mid_measurement[7] ^ mid_measurement[8] ^ mid_measurement[9] ^ mid_measurement[10] ^ mid_measurement[11]) == true) {
  x q[24];
}
mid_measurement[12] = measure q[25];
if (mid_measurement[12]) {
  x q[25];
}
cx q[24], q[25];
final_measurement[24] = measure q[24];
final_measurement[25] = measure q[25];
if ((mid_measurement[0] ^ mid_measurement[1] ^ mid_measurement[2] ^ mid_measurement[3] ^ mid_measurement[4] ^ mid_measurement[5] ^ mid_measurement[6] ^ mid_measurement[7] ^ mid_measurement[8] ^ mid_measurement[9] ^ mid_measurement[10] ^ mid_measurement[11] ^ mid_measurement[12]) == true) {
  x q[26];
}
mid_measurement[13] = measure q[27];
if (mid_measurement[13]) {
  x q[27];
}
cx q[26], q[27];
final_measurement[26] = measure q[26];
final_measurement[27] = measure q[27];
if ((mid_measurement[0] ^ mid_measurement[1] ^ mid_measurement[2] ^ mid_measurement[3] ^ mid_measurement[4] ^ mid_measurement[5] ^ mid_measurement[6] ^ mid_measurement[7] ^ mid_measurement[8] ^ mid_measurement[9] ^ mid_measurement[10] ^ mid_measurement[11] ^ mid_measurement[12] ^ mid_measurement[13]) == true) {
  x q[28];
}
mid_measurement[14] = measure q[29];
if (mid_measurement[14]) {
  x q[29];
}
cx q[28], q[29];
final_measurement[28] = measure q[28];
final_measurement[29] = measure q[29];
if ((mid_measurement[0] ^ mid_measurement[1] ^ mid_measurement[2] ^ mid_measurement[3] ^ mid_measurement[4] ^ mid_measurement[5] ^ mid_measurement[6] ^ mid_measurement[7] ^ mid_measurement[8] ^ mid_measurement[9] ^ mid_measurement[10] ^ mid_measurement[11] ^ mid_measurement[12] ^ mid_measurement[13] ^ mid_measurement[14]) == true) {
  x q[30];
}
mid_measurement[15] = measure q[31];
if (mid_measurement[15]) {
  x q[31];
}
cx q[30], q[31];
final_measurement[30] = measure q[30];
final_measurement[31] = measure q[31];
