OPENQASM 2.0;
include "qelib1.inc";
gate mcphase(param0) q0,q1 { cp(-pi/4) q0,q1; }
gate mcphase_140264578348960(param0) q0,q1 { cp(pi/4) q0,q1; }
gate mcphase_140264578349248(param0) q0,q1 { cp(pi/4) q0,q1; }
gate mcphase_140264578348912(param0) q0,q1 { cp(pi/4) q0,q1; }
gate mcphase_140264578348864(param0) q0,q1 { cp(pi/4) q0,q1; }
gate mcphase_140264578348432(param0) q0,q1 { cp(pi/4) q0,q1; }
gate mcphase_140264578348624(param0) q0,q1 { cp(pi/4) q0,q1; }
gate mcphase_140264578348384(param0) q0,q1 { cp(pi/4) q0,q1; }
gate mcphase_140264578348144(param0) q0,q1 { cp(pi/4) q0,q1; }
gate ccircuit_41_1325 q0,q1,q2,q3,q4 { ccx q0,q1,q2; ccx q0,q1,q4; s q1; h q1; t q1; cx q0,q1; tdg q1; h q1; sdg q1; ccx q0,q2,q1; mcphase(-pi/4) q0,q1; ccx q0,q4,q1; mcphase_140264578348960(pi/4) q0,q1; ccx q0,q2,q1; mcphase(-pi/4) q0,q1; mcphase_140264578349248(pi/4) q0,q2; ccx q0,q4,q1; mcphase_140264578348912(pi/4) q0,q1; s q1; h q1; t q1; cx q0,q1; tdg q1; h q1; sdg q1; ccx q0,q1,q3; s q1; h q1; t q1; cx q0,q1; tdg q1; h q1; sdg q1; ccx q0,q4,q2; mcphase(-pi/4) q0,q2; mcphase_140264578348864(pi/4) q0,q4; ccx q0,q4,q2; ccx q0,q2,q1; mcphase(-pi/4) q0,q1; ccx q0,q4,q1; mcphase_140264578348432(pi/4) q0,q1; ccx q0,q2,q1; mcphase(-pi/4) q0,q1; mcphase_140264578348624(pi/4) q0,q2; ccx q0,q4,q1; mcphase_140264578348384(pi/4) q0,q1; s q1; h q1; t q1; cx q0,q1; tdg q1; h q1; sdg q1; ccx q0,q4,q2; mcphase(-pi/4) q0,q2; mcphase_140264578348144(pi/4) q0,q4; ccx q0,q4,q2; ccx q0,q1,q4; ccx q0,q4,q2; }
qreg a[1];
qreg b[1];
qreg out[2];
qreg helper[1];
creg meas[5];
ccircuit_41_1325 a[0],b[0],out[0],out[1],helper[0];
barrier a[0],b[0],out[0],out[1],helper[0];
measure a[0] -> meas[0];
measure b[0] -> meas[1];
measure out[0] -> meas[2];
measure out[1] -> meas[3];
measure helper[0] -> meas[4];