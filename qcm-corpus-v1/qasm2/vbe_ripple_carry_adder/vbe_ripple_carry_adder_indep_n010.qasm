OPENQASM 2.0;
include "qelib1.inc";
gate gate_Carry q0,q1,q2,q3 { ccx q1,q2,q3; cx q1,q2; ccx q0,q2,q3; }
gate gate_Sum q0,q1,q2 { cx q1,q2; cx q0,q2; }
gate gate_Carry_dg q0,q1,q2,q3 { ccx q0,q2,q3; cx q1,q2; ccx q1,q2,q3; }
qreg cin[1];
qreg a[3];
qreg b[3];
qreg cout[1];
qreg helper[2];
creg meas[10];
gate_Carry cin[0],a[0],b[0],helper[0];
gate_Carry helper[0],a[1],b[1],helper[1];
gate_Carry helper[1],a[2],b[2],cout[0];
cx a[2],b[2];
gate_Sum helper[1],a[2],b[2];
gate_Carry_dg helper[0],a[1],b[1],helper[1];
gate_Sum helper[0],a[1],b[1];
gate_Carry_dg cin[0],a[0],b[0],helper[0];
gate_Sum cin[0],a[0],b[0];
barrier cin[0],a[0],a[1],a[2],b[0],b[1],b[2],cout[0],helper[0],helper[1];
measure cin[0] -> meas[0];
measure a[0] -> meas[1];
measure a[1] -> meas[2];
measure a[2] -> meas[3];
measure b[0] -> meas[4];
measure b[1] -> meas[5];
measure b[2] -> meas[6];
measure cout[0] -> meas[7];
measure helper[0] -> meas[8];
measure helper[1] -> meas[9];