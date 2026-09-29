OPENQASM 2.0;
include "qelib1.inc";
gate circuit_42_1097 q0,q1,q2 { h q2; cp(pi/2) q2,q1; cp(pi/4) q2,q0; h q1; cp(pi/2) q1,q0; h q0; }
gate circuit_42_1097_dg q0,q1,q2 { h q0; cp(-pi/2) q1,q0; h q1; cp(-pi/4) q2,q0; cp(-pi/2) q2,q1; h q2; }
qreg a[3];
qreg b[3];
creg meas[6];
circuit_42_1097 b[0],b[1],b[2];
cp(pi) a[0],b[0];
cp(pi/2) a[0],b[1];
cp(pi/4) a[0],b[2];
cp(pi) a[1],b[1];
cp(pi/2) a[1],b[2];
cp(pi) a[2],b[2];
circuit_42_1097_dg b[0],b[1],b[2];
barrier a[0],a[1],a[2],b[0],b[1],b[2];
measure a[0] -> meas[0];
measure a[1] -> meas[1];
measure a[2] -> meas[2];
measure b[0] -> meas[3];
measure b[1] -> meas[4];
measure b[2] -> meas[5];