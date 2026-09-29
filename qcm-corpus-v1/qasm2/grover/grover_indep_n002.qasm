OPENQASM 2.0;
include "qelib1.inc";
gate mcphase(param0) q0,q1 { cp(pi) q0,q1; }
gate gate_Q q0,q1 { mcphase(pi) q0,q1; h q0; x q0; z q0; x q0; h q0; }
qreg q[1];
qreg flag[1];
creg meas[2];
h q[0];
x flag[0];
gate_Q q[0],flag[0];
barrier q[0],flag[0];
measure q[0] -> meas[0];
measure flag[0] -> meas[1];