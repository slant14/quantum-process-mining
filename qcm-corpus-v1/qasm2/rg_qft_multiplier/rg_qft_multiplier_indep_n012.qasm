OPENQASM 2.0;
include "qelib1.inc";
gate circuit_42_1641 q0,q1,q2,q3,q4,q5 { h q5; cp(pi/2) q5,q4; cp(pi/4) q5,q3; cp(pi/8) q5,q2; cp(pi/16) q5,q1; cp(pi/32) q5,q0; h q4; cp(pi/2) q4,q3; cp(pi/4) q4,q2; cp(pi/8) q4,q1; cp(pi/16) q4,q0; h q3; cp(pi/2) q3,q2; cp(pi/4) q3,q1; cp(pi/8) q3,q0; h q2; cp(pi/2) q2,q1; cp(pi/4) q2,q0; h q1; cp(pi/2) q1,q0; h q0; }
gate mcphase(param0) q0,q1,q2 { cx q0,q2; rz(-4*pi) q2; cx q1,q2; rz(4*pi) q2; cx q0,q2; rz(-4*pi) q2; cx q1,q2; rz(4*pi) q2; crz(8*pi) q0,q1; p(4*pi) q0; }
gate mcphase_140264582964736(param0) q0,q1,q2 { cx q0,q2; rz(-2*pi) q2; cx q1,q2; rz(2*pi) q2; cx q0,q2; rz(-2*pi) q2; cx q1,q2; rz(2*pi) q2; crz(4*pi) q0,q1; p(2*pi) q0; }
gate mcphase_140264578021856(param0) q0,q1,q2 { cx q0,q2; rz(-pi) q2; cx q1,q2; rz(pi) q2; cx q0,q2; rz(-pi) q2; cx q1,q2; rz(pi) q2; crz(2*pi) q0,q1; p(pi) q0; }
gate mcphase_140264578020416(param0) q0,q1,q2 { cx q0,q2; rz(-pi/2) q2; cx q1,q2; rz(pi/2) q2; cx q0,q2; rz(-pi/2) q2; cx q1,q2; rz(pi/2) q2; crz(pi) q0,q1; p(pi/2) q0; }
gate mcphase_140264578021616(param0) q0,q1,q2 { cx q0,q2; rz(-pi/4) q2; cx q1,q2; rz(pi/4) q2; cx q0,q2; rz(-pi/4) q2; cx q1,q2; rz(pi/4) q2; crz(pi/2) q0,q1; p(pi/4) q0; }
gate mcphase_140264578020608(param0) q0,q1,q2 { cx q0,q2; rz(-pi/8) q2; cx q1,q2; rz(pi/8) q2; cx q0,q2; rz(-pi/8) q2; cx q1,q2; rz(pi/8) q2; crz(pi/4) q0,q1; p(pi/8) q0; }
gate mcphase_140264578020224(param0) q0,q1,q2 { cx q0,q2; rz(-2*pi) q2; cx q1,q2; rz(2*pi) q2; cx q0,q2; rz(-2*pi) q2; cx q1,q2; rz(2*pi) q2; crz(4*pi) q0,q1; p(2*pi) q0; }
gate mcphase_140264578020128(param0) q0,q1,q2 { cx q0,q2; rz(-pi) q2; cx q1,q2; rz(pi) q2; cx q0,q2; rz(-pi) q2; cx q1,q2; rz(pi) q2; crz(2*pi) q0,q1; p(pi) q0; }
gate mcphase_140264578020032(param0) q0,q1,q2 { cx q0,q2; rz(-pi/2) q2; cx q1,q2; rz(pi/2) q2; cx q0,q2; rz(-pi/2) q2; cx q1,q2; rz(pi/2) q2; crz(pi) q0,q1; p(pi/2) q0; }
gate mcphase_140264578018688(param0) q0,q1,q2 { cx q0,q2; rz(-pi/4) q2; cx q1,q2; rz(pi/4) q2; cx q0,q2; rz(-pi/4) q2; cx q1,q2; rz(pi/4) q2; crz(pi/2) q0,q1; p(pi/4) q0; }
gate mcphase_140264578019792(param0) q0,q1,q2 { cx q0,q2; rz(-pi/8) q2; cx q1,q2; rz(pi/8) q2; cx q0,q2; rz(-pi/8) q2; cx q1,q2; rz(pi/8) q2; crz(pi/4) q0,q1; p(pi/8) q0; }
gate mcphase_140264578019600(param0) q0,q1,q2 { cx q0,q2; rz(-pi/16) q2; cx q1,q2; rz(pi/16) q2; cx q0,q2; rz(-pi/16) q2; cx q1,q2; rz(pi/16) q2; crz(pi/8) q0,q1; p(pi/16) q0; }
gate mcphase_140264578019408(param0) q0,q1,q2 { cx q0,q2; rz(-pi) q2; cx q1,q2; rz(pi) q2; cx q0,q2; rz(-pi) q2; cx q1,q2; rz(pi) q2; crz(2*pi) q0,q1; p(pi) q0; }
gate mcphase_140264578018016(param0) q0,q1,q2 { cx q0,q2; rz(-2*pi) q2; cx q1,q2; rz(2*pi) q2; cx q0,q2; rz(-2*pi) q2; cx q1,q2; rz(2*pi) q2; crz(4*pi) q0,q1; p(2*pi) q0; }
gate mcphase_140264578019120(param0) q0,q1,q2 { cx q0,q2; rz(-pi/2) q2; cx q1,q2; rz(pi/2) q2; cx q0,q2; rz(-pi/2) q2; cx q1,q2; rz(pi/2) q2; crz(pi) q0,q1; p(pi/2) q0; }
gate mcphase_140264578018112(param0) q0,q1,q2 { cx q0,q2; rz(-pi) q2; cx q1,q2; rz(pi) q2; cx q0,q2; rz(-pi) q2; cx q1,q2; rz(pi) q2; crz(2*pi) q0,q1; p(pi) q0; }
gate mcphase_140264578019024(param0) q0,q1,q2 { cx q0,q2; rz(-pi/4) q2; cx q1,q2; rz(pi/4) q2; cx q0,q2; rz(-pi/4) q2; cx q1,q2; rz(pi/4) q2; crz(pi/2) q0,q1; p(pi/4) q0; }
gate mcphase_140264578018208(param0) q0,q1,q2 { cx q0,q2; rz(-pi/2) q2; cx q1,q2; rz(pi/2) q2; cx q0,q2; rz(-pi/2) q2; cx q1,q2; rz(pi/2) q2; crz(pi) q0,q1; p(pi/2) q0; }
gate mcphase_140264578018928(param0) q0,q1,q2 { cx q0,q2; rz(-pi/8) q2; cx q1,q2; rz(pi/8) q2; cx q0,q2; rz(-pi/8) q2; cx q1,q2; rz(pi/8) q2; crz(pi/4) q0,q1; p(pi/8) q0; }
gate mcphase_140264578018304(param0) q0,q1,q2 { cx q0,q2; rz(-pi/4) q2; cx q1,q2; rz(pi/4) q2; cx q0,q2; rz(-pi/4) q2; cx q1,q2; rz(pi/4) q2; crz(pi/2) q0,q1; p(pi/4) q0; }
gate mcphase_140264578018832(param0) q0,q1,q2 { cx q0,q2; rz(-pi/16) q2; cx q1,q2; rz(pi/16) q2; cx q0,q2; rz(-pi/16) q2; cx q1,q2; rz(pi/16) q2; crz(pi/8) q0,q1; p(pi/16) q0; }
gate mcphase_140264583147552(param0) q0,q1,q2 { cx q0,q2; rz(-pi/8) q2; cx q1,q2; rz(pi/8) q2; cx q0,q2; rz(-pi/8) q2; cx q1,q2; rz(pi/8) q2; crz(pi/4) q0,q1; p(pi/8) q0; }
gate mcphase_140264578018736(param0) q0,q1,q2 { cx q0,q2; rz(-pi/32) q2; cx q1,q2; rz(pi/32) q2; cx q0,q2; rz(-pi/32) q2; cx q1,q2; rz(pi/32) q2; crz(pi/16) q0,q1; p(pi/32) q0; }
gate mcphase_140264580344880(param0) q0,q1,q2 { cx q0,q2; rz(-pi/16) q2; cx q1,q2; rz(pi/16) q2; cx q0,q2; rz(-pi/16) q2; cx q1,q2; rz(pi/16) q2; crz(pi/8) q0,q1; p(pi/16) q0; }
gate mcphase_140264581254896(param0) q0,q1,q2 { cx q0,q2; rz(-pi) q2; cx q1,q2; rz(pi) q2; cx q0,q2; rz(-pi) q2; cx q1,q2; rz(pi) q2; crz(2*pi) q0,q1; p(pi) q0; }
gate mcphase_140264578451360(param0) q0,q1,q2 { cx q0,q2; rz(-pi/2) q2; cx q1,q2; rz(pi/2) q2; cx q0,q2; rz(-pi/2) q2; cx q1,q2; rz(pi/2) q2; crz(pi) q0,q1; p(pi/2) q0; }
gate mcphase_140264578451408(param0) q0,q1,q2 { cx q0,q2; rz(-pi/4) q2; cx q1,q2; rz(pi/4) q2; cx q0,q2; rz(-pi/4) q2; cx q1,q2; rz(pi/4) q2; crz(pi/2) q0,q1; p(pi/4) q0; }
gate mcphase_140264578451504(param0) q0,q1,q2 { cx q0,q2; rz(-pi/8) q2; cx q1,q2; rz(pi/8) q2; cx q0,q2; rz(-pi/8) q2; cx q1,q2; rz(pi/8) q2; crz(pi/4) q0,q1; p(pi/8) q0; }
gate mcphase_140264578451600(param0) q0,q1,q2 { cx q0,q2; rz(-pi/16) q2; cx q1,q2; rz(pi/16) q2; cx q0,q2; rz(-pi/16) q2; cx q1,q2; rz(pi/16) q2; crz(pi/8) q0,q1; p(pi/16) q0; }
gate mcphase_140264578451696(param0) q0,q1,q2 { cx q0,q2; rz(-pi/32) q2; cx q1,q2; rz(pi/32) q2; cx q0,q2; rz(-pi/32) q2; cx q1,q2; rz(pi/32) q2; crz(pi/16) q0,q1; p(pi/32) q0; }
gate mcphase_140264578451792(param0) q0,q1,q2 { cx q0,q2; rz(-pi/2) q2; cx q1,q2; rz(pi/2) q2; cx q0,q2; rz(-pi/2) q2; cx q1,q2; rz(pi/2) q2; crz(pi) q0,q1; p(pi/2) q0; }
gate mcphase_140264578452368(param0) q0,q1,q2 { cx q0,q2; rz(-pi) q2; cx q1,q2; rz(pi) q2; cx q0,q2; rz(-pi) q2; cx q1,q2; rz(pi) q2; crz(2*pi) q0,q1; p(pi) q0; }
gate mcphase_140264578451888(param0) q0,q1,q2 { cx q0,q2; rz(-pi/4) q2; cx q1,q2; rz(pi/4) q2; cx q0,q2; rz(-pi/4) q2; cx q1,q2; rz(pi/4) q2; crz(pi/2) q0,q1; p(pi/4) q0; }
gate mcphase_140264578452464(param0) q0,q1,q2 { cx q0,q2; rz(-pi/2) q2; cx q1,q2; rz(pi/2) q2; cx q0,q2; rz(-pi/2) q2; cx q1,q2; rz(pi/2) q2; crz(pi) q0,q1; p(pi/2) q0; }
gate mcphase_140264578451984(param0) q0,q1,q2 { cx q0,q2; rz(-pi/8) q2; cx q1,q2; rz(pi/8) q2; cx q0,q2; rz(-pi/8) q2; cx q1,q2; rz(pi/8) q2; crz(pi/4) q0,q1; p(pi/8) q0; }
gate mcphase_140264578452560(param0) q0,q1,q2 { cx q0,q2; rz(-pi/4) q2; cx q1,q2; rz(pi/4) q2; cx q0,q2; rz(-pi/4) q2; cx q1,q2; rz(pi/4) q2; crz(pi/2) q0,q1; p(pi/4) q0; }
gate mcphase_140264578452080(param0) q0,q1,q2 { cx q0,q2; rz(-pi/16) q2; cx q1,q2; rz(pi/16) q2; cx q0,q2; rz(-pi/16) q2; cx q1,q2; rz(pi/16) q2; crz(pi/8) q0,q1; p(pi/16) q0; }
gate mcphase_140264578452656(param0) q0,q1,q2 { cx q0,q2; rz(-pi/8) q2; cx q1,q2; rz(pi/8) q2; cx q0,q2; rz(-pi/8) q2; cx q1,q2; rz(pi/8) q2; crz(pi/4) q0,q1; p(pi/8) q0; }
gate mcphase_140264578452176(param0) q0,q1,q2 { cx q0,q2; rz(-pi/32) q2; cx q1,q2; rz(pi/32) q2; cx q0,q2; rz(-pi/32) q2; cx q1,q2; rz(pi/32) q2; crz(pi/16) q0,q1; p(pi/32) q0; }
gate mcphase_140264578452752(param0) q0,q1,q2 { cx q0,q2; rz(-pi/16) q2; cx q1,q2; rz(pi/16) q2; cx q0,q2; rz(-pi/16) q2; cx q1,q2; rz(pi/16) q2; crz(pi/8) q0,q1; p(pi/16) q0; }
gate mcphase_140264578452272(param0) q0,q1,q2 { cx q0,q2; rz(-pi/64) q2; cx q1,q2; rz(pi/64) q2; cx q0,q2; rz(-pi/64) q2; cx q1,q2; rz(pi/64) q2; crz(pi/32) q0,q1; p(pi/64) q0; }
gate mcphase_140264578452848(param0) q0,q1,q2 { cx q0,q2; rz(-pi/32) q2; cx q1,q2; rz(pi/32) q2; cx q0,q2; rz(-pi/32) q2; cx q1,q2; rz(pi/32) q2; crz(pi/16) q0,q1; p(pi/32) q0; }
gate mcphase_140264578452944(param0) q0,q1,q2 { cx q0,q2; rz(-pi/2) q2; cx q1,q2; rz(pi/2) q2; cx q0,q2; rz(-pi/2) q2; cx q1,q2; rz(pi/2) q2; crz(pi) q0,q1; p(pi/2) q0; }
gate mcphase_140264578453040(param0) q0,q1,q2 { cx q0,q2; rz(-pi/4) q2; cx q1,q2; rz(pi/4) q2; cx q0,q2; rz(-pi/4) q2; cx q1,q2; rz(pi/4) q2; crz(pi/2) q0,q1; p(pi/4) q0; }
gate mcphase_140264578453136(param0) q0,q1,q2 { cx q0,q2; rz(-pi/8) q2; cx q1,q2; rz(pi/8) q2; cx q0,q2; rz(-pi/8) q2; cx q1,q2; rz(pi/8) q2; crz(pi/4) q0,q1; p(pi/8) q0; }
gate mcphase_140264578453232(param0) q0,q1,q2 { cx q0,q2; rz(-pi/16) q2; cx q1,q2; rz(pi/16) q2; cx q0,q2; rz(-pi/16) q2; cx q1,q2; rz(pi/16) q2; crz(pi/8) q0,q1; p(pi/16) q0; }
gate mcphase_140264578453328(param0) q0,q1,q2 { cx q0,q2; rz(-pi/32) q2; cx q1,q2; rz(pi/32) q2; cx q0,q2; rz(-pi/32) q2; cx q1,q2; rz(pi/32) q2; crz(pi/16) q0,q1; p(pi/32) q0; }
gate mcphase_140264578453424(param0) q0,q1,q2 { cx q0,q2; rz(-pi/64) q2; cx q1,q2; rz(pi/64) q2; cx q0,q2; rz(-pi/64) q2; cx q1,q2; rz(pi/64) q2; crz(pi/32) q0,q1; p(pi/64) q0; }
gate mcphase_140264578453520(param0) q0,q1,q2 { cx q0,q2; rz(-pi/4) q2; cx q1,q2; rz(pi/4) q2; cx q0,q2; rz(-pi/4) q2; cx q1,q2; rz(pi/4) q2; crz(pi/2) q0,q1; p(pi/4) q0; }
gate mcphase_140264578453616(param0) q0,q1,q2 { cx q0,q2; rz(-pi/8) q2; cx q1,q2; rz(pi/8) q2; cx q0,q2; rz(-pi/8) q2; cx q1,q2; rz(pi/8) q2; crz(pi/4) q0,q1; p(pi/8) q0; }
gate mcphase_140264578453712(param0) q0,q1,q2 { cx q0,q2; rz(-pi/16) q2; cx q1,q2; rz(pi/16) q2; cx q0,q2; rz(-pi/16) q2; cx q1,q2; rz(pi/16) q2; crz(pi/8) q0,q1; p(pi/16) q0; }
gate mcphase_140264578453808(param0) q0,q1,q2 { cx q0,q2; rz(-pi/32) q2; cx q1,q2; rz(pi/32) q2; cx q0,q2; rz(-pi/32) q2; cx q1,q2; rz(pi/32) q2; crz(pi/16) q0,q1; p(pi/32) q0; }
gate mcphase_140264578453904(param0) q0,q1,q2 { cx q0,q2; rz(-pi/64) q2; cx q1,q2; rz(pi/64) q2; cx q0,q2; rz(-pi/64) q2; cx q1,q2; rz(pi/64) q2; crz(pi/32) q0,q1; p(pi/64) q0; }
gate mcphase_140264578454000(param0) q0,q1,q2 { cx q0,q2; rz(-0.02454369260617026) q2; cx q1,q2; rz(0.02454369260617026) q2; cx q0,q2; rz(-0.02454369260617026) q2; cx q1,q2; rz(0.02454369260617026) q2; crz(pi/64) q0,q1; p(0.02454369260617026) q0; }
gate circuit_42_1641_dg q0,q1,q2,q3,q4,q5 { h q0; cp(-pi/2) q1,q0; h q1; cp(-pi/4) q2,q0; cp(-pi/2) q2,q1; h q2; cp(-pi/8) q3,q0; cp(-pi/4) q3,q1; cp(-pi/2) q3,q2; h q3; cp(-pi/16) q4,q0; cp(-pi/8) q4,q1; cp(-pi/4) q4,q2; cp(-pi/2) q4,q3; h q4; cp(-pi/32) q5,q0; cp(-pi/16) q5,q1; cp(-pi/8) q5,q2; cp(-pi/4) q5,q3; cp(-pi/2) q5,q4; h q5; }
qreg a[3];
qreg b[3];
qreg out[6];
creg meas[12];
circuit_42_1641 out[0],out[1],out[2],out[3],out[4],out[5];
mcphase(16*pi) a[2],b[2],out[0];
mcphase_140264582964736(8*pi) a[2],b[2],out[1];
mcphase_140264578021856(4*pi) a[2],b[2],out[2];
mcphase_140264578020416(2*pi) a[2],b[2],out[3];
mcphase_140264578021616(pi) a[2],b[2],out[4];
mcphase_140264578020608(pi/2) a[2],b[2],out[5];
mcphase_140264578020224(8*pi) a[2],b[1],out[0];
mcphase_140264578020128(4*pi) a[2],b[1],out[1];
mcphase_140264578020032(2*pi) a[2],b[1],out[2];
mcphase_140264578018688(pi) a[2],b[1],out[3];
mcphase_140264578019792(pi/2) a[2],b[1],out[4];
mcphase_140264578019600(pi/4) a[2],b[1],out[5];
mcphase_140264578019408(4*pi) a[2],b[0],out[0];
mcphase_140264578018016(8*pi) a[1],b[2],out[0];
mcphase_140264578019120(2*pi) a[2],b[0],out[1];
mcphase_140264578018112(4*pi) a[1],b[2],out[1];
mcphase_140264578019024(pi) a[2],b[0],out[2];
mcphase_140264578018208(2*pi) a[1],b[2],out[2];
mcphase_140264578018928(pi/2) a[2],b[0],out[3];
mcphase_140264578018304(pi) a[1],b[2],out[3];
mcphase_140264578018832(pi/4) a[2],b[0],out[4];
mcphase_140264583147552(pi/2) a[1],b[2],out[4];
mcphase_140264578018736(pi/8) a[2],b[0],out[5];
mcphase_140264580344880(pi/4) a[1],b[2],out[5];
mcphase_140264581254896(4*pi) a[1],b[1],out[0];
mcphase_140264578451360(2*pi) a[1],b[1],out[1];
mcphase_140264578451408(pi) a[1],b[1],out[2];
mcphase_140264578451504(pi/2) a[1],b[1],out[3];
mcphase_140264578451600(pi/4) a[1],b[1],out[4];
mcphase_140264578451696(pi/8) a[1],b[1],out[5];
mcphase_140264578451792(2*pi) a[1],b[0],out[0];
mcphase_140264578452368(4*pi) a[0],b[2],out[0];
mcphase_140264578451888(pi) a[1],b[0],out[1];
mcphase_140264578452464(2*pi) a[0],b[2],out[1];
mcphase_140264578451984(pi/2) a[1],b[0],out[2];
mcphase_140264578452560(pi) a[0],b[2],out[2];
mcphase_140264578452080(pi/4) a[1],b[0],out[3];
mcphase_140264578452656(pi/2) a[0],b[2],out[3];
mcphase_140264578452176(pi/8) a[1],b[0],out[4];
mcphase_140264578452752(pi/4) a[0],b[2],out[4];
mcphase_140264578452272(pi/16) a[1],b[0],out[5];
mcphase_140264578452848(pi/8) a[0],b[2],out[5];
mcphase_140264578452944(2*pi) a[0],b[1],out[0];
mcphase_140264578453040(pi) a[0],b[1],out[1];
mcphase_140264578453136(pi/2) a[0],b[1],out[2];
mcphase_140264578453232(pi/4) a[0],b[1],out[3];
mcphase_140264578453328(pi/8) a[0],b[1],out[4];
mcphase_140264578453424(pi/16) a[0],b[1],out[5];
mcphase_140264578453520(pi) a[0],b[0],out[0];
mcphase_140264578453616(pi/2) a[0],b[0],out[1];
mcphase_140264578453712(pi/4) a[0],b[0],out[2];
mcphase_140264578453808(pi/8) a[0],b[0],out[3];
mcphase_140264578453904(pi/16) a[0],b[0],out[4];
mcphase_140264578454000(pi/32) a[0],b[0],out[5];
circuit_42_1641_dg out[0],out[1],out[2],out[3],out[4],out[5];
barrier a[0],a[1],a[2],b[0],b[1],b[2],out[0],out[1],out[2],out[3],out[4],out[5];
measure a[0] -> meas[0];
measure a[1] -> meas[1];
measure a[2] -> meas[2];
measure b[0] -> meas[3];
measure b[1] -> meas[4];
measure b[2] -> meas[5];
measure out[0] -> meas[6];
measure out[1] -> meas[7];
measure out[2] -> meas[8];
measure out[3] -> meas[9];
measure out[4] -> meas[10];
measure out[5] -> meas[11];