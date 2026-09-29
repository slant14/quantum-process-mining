OPENQASM 2.0;
include "qelib1.inc";
gate qft_dg q0,q1 { swap q0,q1; h q0; cp(-pi/2) q1,q0; h q1; }
qreg q[4];
creg meas[4];
h q[3];
cp(pi/2) q[3],q[2];
h q[2];
swap q[2],q[3];
cp(pi) q[0],q[3];
cp(pi/2) q[0],q[2];
cp(pi) q[1],q[2];
qft_dg q[2],q[3];
barrier q[0],q[1],q[2],q[3];
measure q[0] -> meas[0];
measure q[1] -> meas[1];
measure q[2] -> meas[2];
measure q[3] -> meas[3];