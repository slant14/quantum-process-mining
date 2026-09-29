OPENQASM 2.0;
include "qelib1.inc";
gate circuit_42_1093 q0,q1 { h q1; cp(pi/2) q1,q0; h q0; }
gate circuit_42_1093_dg q0,q1 { h q0; cp(-pi/2) q1,q0; h q1; }
qreg a[2];
qreg b[2];
creg meas[4];
circuit_42_1093 b[0],b[1];
cp(pi) a[0],b[0];
cp(pi/2) a[0],b[1];
cp(pi) a[1],b[1];
circuit_42_1093_dg b[0],b[1];
barrier a[0],a[1],b[0],b[1];
measure a[0] -> meas[0];
measure a[1] -> meas[1];
measure b[0] -> meas[2];
measure b[1] -> meas[3];