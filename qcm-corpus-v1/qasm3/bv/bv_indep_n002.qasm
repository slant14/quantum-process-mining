OPENQASM 3.0;
include "stdgates.inc";
bit[1] c;
qubit[2] q;
x q[0];
h q[1];
h q[1];
c[0] = measure q[1];
