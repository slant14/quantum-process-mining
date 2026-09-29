OPENQASM 3.0;
include "stdgates.inc";
gate qft_dg _gate_q_0 {
  h _gate_q_0;
}
bit[1] c;
qubit[1] sys;
qubit[1] phase_0;
qubit[1] ancilla;
x sys[0];
h phase_0[0];
cp(11.366282220687872) phase_0[0], sys[0];
qft_dg phase_0[0];
cry(1.1714210053478946) phase_0[0], ancilla[0];
h phase_0[0];
cp(-11.366282220687872) phase_0[0], sys[0];
h phase_0[0];
c[0] = measure sys[0];
