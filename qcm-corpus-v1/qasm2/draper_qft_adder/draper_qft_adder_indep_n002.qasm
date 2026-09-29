OPENQASM 2.0;
include "qelib1.inc";
gate circuit_42_1089 q0 { h q0; }
gate circuit_42_1089_dg q0 { h q0; }
qreg a[1];
qreg b[1];
creg meas[2];
circuit_42_1089 b[0];
cp(pi) a[0],b[0];
circuit_42_1089_dg b[0];
barrier a[0],b[0];
measure a[0] -> meas[0];
measure b[0] -> meas[1];