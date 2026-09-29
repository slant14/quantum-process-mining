OPENQASM 2.0;
include "qelib1.inc";
gate gate_MAJ q0,q1,q2 { cx q0,q1; cx q0,q2; ccx q2,q1,q0; }
gate gate_UMA q0,q1,q2 { ccx q2,q1,q0; cx q0,q2; cx q2,q1; }
qreg cin[1];
qreg a[2];
qreg b[2];
qreg cout[1];
creg meas[6];
gate_MAJ a[0],b[0],cin[0];
gate_MAJ a[1],b[1],a[0];
cx a[1],cout[0];
gate_UMA a[1],b[1],a[0];
gate_UMA a[0],b[0],cin[0];
barrier cin[0],a[0],a[1],b[0],b[1],cout[0];
measure cin[0] -> meas[0];
measure a[0] -> meas[1];
measure a[1] -> meas[2];
measure b[0] -> meas[3];
measure b[1] -> meas[4];
measure cout[0] -> meas[5];