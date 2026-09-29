OPENQASM 3.0;
include "stdgates.inc";
gate _circuit_42_1629 _gate_q_0, _gate_q_1 {
  h _gate_q_1;
  cp(pi/2) _gate_q_1, _gate_q_0;
  h _gate_q_0;
}
gate mcphase(_gate_p_0) _gate_q_0, _gate_q_1, _gate_q_2 {
  cx _gate_q_0, _gate_q_2;
  rz(-pi/4) _gate_q_2;
  cx _gate_q_1, _gate_q_2;
  rz(pi/4) _gate_q_2;
  cx _gate_q_0, _gate_q_2;
  rz(-pi/4) _gate_q_2;
  cx _gate_q_1, _gate_q_2;
  rz(pi/4) _gate_q_2;
  crz(pi/2) _gate_q_0, _gate_q_1;
  p(pi/4) _gate_q_0;
}
gate mcphase_0(_gate_p_0) _gate_q_0, _gate_q_1, _gate_q_2 {
  cx _gate_q_0, _gate_q_2;
  rz(-pi/8) _gate_q_2;
  cx _gate_q_1, _gate_q_2;
  rz(pi/8) _gate_q_2;
  cx _gate_q_0, _gate_q_2;
  rz(-pi/8) _gate_q_2;
  cx _gate_q_1, _gate_q_2;
  rz(pi/8) _gate_q_2;
  crz(pi/4) _gate_q_0, _gate_q_1;
  p(pi/8) _gate_q_0;
}
gate _circuit_42_1629_dg _gate_q_0, _gate_q_1 {
  h _gate_q_0;
  cp(-pi/2) _gate_q_1, _gate_q_0;
  h _gate_q_1;
}
bit[4] meas;
qubit[1] a;
qubit[1] b;
qubit[2] out;
_circuit_42_1629 out[0], out[1];
mcphase(pi) a[0], b[0], out[0];
mcphase_0(pi/2) a[0], b[0], out[1];
_circuit_42_1629_dg out[0], out[1];
barrier a[0], b[0], out[0], out[1];
meas[0] = measure a[0];
meas[1] = measure b[0];
meas[2] = measure out[0];
meas[3] = measure out[1];
