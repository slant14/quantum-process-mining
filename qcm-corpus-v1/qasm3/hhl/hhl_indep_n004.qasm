OPENQASM 3.0;
include "stdgates.inc";
gate qft_dg _gate_q_0, _gate_q_1 {
  swap _gate_q_0, _gate_q_1;
  h _gate_q_0;
  cp(-pi/2) _gate_q_1, _gate_q_0;
  h _gate_q_1;
}
bit[1] c;
qubit[1] sys;
qubit[2] phase_0;
qubit[1] ancilla;
x sys[0];
h phase_0[0];
cp(11.366282220687872) phase_0[0], sys[0];
h phase_0[1];
cp(5.683141110343936) phase_0[1], sys[0];
qft_dg phase_0[0], phase_0[1];
cry(pi) phase_0[0], ancilla[0];
cry(1.1714210053478946) phase_0[1], ancilla[0];
h phase_0[1];
cp(pi/2) phase_0[1], phase_0[0];
h phase_0[0];
swap phase_0[0], phase_0[1];
cp(-5.683141110343936) phase_0[1], sys[0];
cp(-11.366282220687872) phase_0[0], sys[0];
h phase_0[0];
h phase_0[1];
c[0] = measure sys[0];
