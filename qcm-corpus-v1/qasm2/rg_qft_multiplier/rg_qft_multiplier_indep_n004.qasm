OPENQASM 2.0;
include "qelib1.inc";
gate circuit_42_1629 q0,q1 { h q1; cp(pi/2) q1,q0; h q0; }
gate mcphase(param0) q0,q1,q2 { cx q0,q2; rz(-pi/4) q2; cx q1,q2; rz(pi/4) q2; cx q0,q2; rz(-pi/4) q2; cx q1,q2; rz(pi/4) q2; crz(pi/2) q0,q1; p(pi/4) q0; }
gate mcphase_140264579114016(param0) q0,q1,q2 { cx q0,q2; rz(-pi/8) q2; cx q1,q2; rz(pi/8) q2; cx q0,q2; rz(-pi/8) q2; cx q1,q2; rz(pi/8) q2; crz(pi/4) q0,q1; p(pi/8) q0; }
gate circuit_42_1629_dg q0,q1 { h q0; cp(-pi/2) q1,q0; h q1; }
qreg a[1];
qreg b[1];
qreg out[2];
creg meas[4];
circuit_42_1629 out[0],out[1];
mcphase(pi) a[0],b[0],out[0];
mcphase_140264579114016(pi/2) a[0],b[0],out[1];
circuit_42_1629_dg out[0],out[1];
barrier a[0],b[0],out[0],out[1];
measure a[0] -> meas[0];
measure b[0] -> meas[1];
measure out[0] -> meas[2];
measure out[1] -> meas[3];