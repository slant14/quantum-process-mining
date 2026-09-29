OPENQASM 2.0;
include "qelib1.inc";
gate gate_Carry q0,q1,q2,q3 { ccx q1,q2,q3; cx q1,q2; ccx q0,q2,q3; }
gate gate_Sum q0,q1,q2 { cx q1,q2; cx q0,q2; }
qreg cin[1];
qreg a[1];
qreg b[1];
qreg cout[1];
creg meas[4];
gate_Carry cin[0],a[0],b[0],cout[0];
cx a[0],b[0];
gate_Sum cin[0],a[0],b[0];
barrier cin[0],a[0],b[0],cout[0];
measure cin[0] -> meas[0];
measure a[0] -> meas[1];
measure b[0] -> meas[2];
measure cout[0] -> meas[3];