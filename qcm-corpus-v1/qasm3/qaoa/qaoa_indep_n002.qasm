OPENQASM 3.0;
include "stdgates.inc";
gate rzz(p0) _gate_q_0, _gate_q_1 {
  cx _gate_q_0, _gate_q_1;
  rz(p0) _gate_q_1;
  cx _gate_q_0, _gate_q_1;
}
qubit[2] q;
h q[0];
h q[1];
rzz(10.410545461930019) q[0], q[1];
rx(12.013471791158686) q[0];
rx(12.013471791158686) q[1];
rzz(1.8759344847470487) q[0], q[1];
rx(2.609806595315514) q[0];
rx(2.609806595315514) q[1];
