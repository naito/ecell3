# Arkin, A. and J. Ross (1995). "Statistical Construction of Chemical-Reaction Mechanisms from Measured Time-Series." Journal of Physical Chemistry 99(3): 970-979.
# Gennemark, P. and D. Wedelin (2007). "Efficient algorithms for ordinary differential equation model identification of biological systems." IET Syst Biol 1(2): 120-129.
# Gennemark, P. and D. Wedelin (2009). "Benchmarks for identification of ordinary differential equations from time series data." Bioinformatics 25(6): 780-786.
# http://odeidentification.org
# http://www.cse.chalmers.se/~dag/identification/Benchmarks/metabol.html

name = 'Arkin_95'

em = '''
Stepper ODE45Stepper( Default )
{
	# no property
}

System System( / )
{
	StepperID	Default;
	Name	default;

	Variable Variable( Dimensions )
	{
		Value	3;
	}
	
	Variable Variable( SIZE )
	{
		Value	1.0;
		Fixed	1;
	}
	
	Variable Variable( s1 )
	{
		Name	s1;
		Value	2.0;
		Fixed	0;
	}
	
	Variable Variable( s2 )
	{
		Name	s2;
		Value	30.0;
		Fixed	0;
	}
	
	Variable Variable( s3 )
	{
		Name	s3;
		Value	1.2482071;
		Fixed	0;
	}
	
	Variable Variable( s4 )
	{
		Name	s4;
		Value	49.375896;
		Fixed	0;
	}
	
	Variable Variable( s5 )
	{
		Name	s5;
		Value	49.375896;
		Fixed	0;
	}
	
	Variable Variable( s6 )
	{
		Name	s6;
		Value	98.638884;
		Fixed	0;
	}
	
	Variable Variable( s7 )
	{
		Name	s7;
		Value	1.3611157;
		Fixed	0;
	}
	
	Process ExpressionFluxProcess( re31 )
	{
		Name	"-> [s3]; { s2 };";
		k31	-5.0;
		km31	5.0;
		ki31	1.0;
		Expression	"s3.NumberConc * k31 / (s3.NumberConc + km31) / (1 + s2.NumberConc / ki31)";
		VariableReferenceList
			[ s3 Variable:/:s3 1 ]
			[ s2 Variable:/:s2 0 ];
	}
	
	Process ExpressionFluxProcess( re32 )
	{
		Name	"-> [s3]; { s1 };";
		k32	-5.0;
		km32	5.0;
		ki32	1.0;
		Expression	"s3.NumberConc * k32 / (s3.NumberConc + km32) / (1 + s1.NumberConc / ki32)";
		VariableReferenceList
			[ s3 Variable:/:s3 1 ]
			[ s1 Variable:/:s1 0 ];
	}
	
	Process ExpressionFluxProcess( re33 )
	{
		Name	"-> [s3]; { s4 };";
		k33	1.0;
		km33	5.0;
		Expression	"k33 * s4.NumberConc / (km33 + s4.NumberConc)";
		VariableReferenceList
			[ s3 Variable:/:s3 1 ]
			[ s4 Variable:/:s4 0 ];
	}
	
	Process ExpressionFluxProcess( re34 )
	{
		Name	"-> [s3]; { s5 };";
		k34	1.0;
		km34	5.0;
		Expression	"k34 * s5.NumberConc / (km34 + s5.NumberConc)";
		VariableReferenceList
			[ s3 Variable:/:s3 1 ]
			[ s5 Variable:/:s5 0 ];
	}
	
	Process ExpressionFluxProcess( re41 )
	{
		Name	"-> [s4]; { s3, s1 };";
		k41	5.0;
		km41	5.0;
		ki41	1.0;
		Expression	"s3.NumberConc * k41 / (s3.NumberConc + km41) / (1 + s1.NumberConc / ki41)";
		VariableReferenceList
			[ s4 Variable:/:s4 1 ]
			[ s3 Variable:/:s3 0 ]
			[ s1 Variable:/:s1 0 ];
	}
	
	Process ExpressionFluxProcess( re42 )
	{
		Name	"-> [s4];";
		k42	-1.0;
		km42	5.0;
		Expression	"k42 * s4.NumberConc / (km42 + s4.NumberConc)";
		VariableReferenceList
			[ s4 Variable:/:s4 1 ];
	}
	
	Process ExpressionFluxProcess( re51 )
	{
		Name	"-> [s5]; { s3, s2 };";
		k51	5.0;
		km51	5.0;
		ki51	1.0;
		Expression	"s3.NumberConc * k51 / (s3.NumberConc + km51) / (1 + s2.NumberConc / ki51)";
		VariableReferenceList
			[ s5 Variable:/:s5 1 ]
			[ s3 Variable:/:s3 0 ]
			[ s2 Variable:/:s2 0 ];
	}
	
	Process ExpressionFluxProcess( re52 )
	{
		Name	"-> [s5];";
		k52	-1.0;
		km52	5.0;
		Expression	"k52 * s5.NumberConc / (km52 + s5.NumberConc)";
		VariableReferenceList
			[ s5 Variable:/:s5 1 ];
	}
	
	Process ExpressionFluxProcess( re61 )
	{
		Name	"-> [s6]; { s7, s3 };";
		k61	10.0;
		km61	5.0;
		ki61	1.0;
		Expression	"s7.NumberConc * k61 / (s7.NumberConc + km61) / (1 + s3.NumberConc / ki61)";
		VariableReferenceList
			[ s6 Variable:/:s6 1 ]
			[ s7 Variable:/:s7 0 ]
			[ s3 Variable:/:s3 0 ];
	}
	
	Process ExpressionFluxProcess( re62 )
	{
		Name	"-> [s6];";
		k62	-1.0;
		km62	5.0;
		Expression	"k62 * s6.NumberConc / (km62 + s6.NumberConc)";
		VariableReferenceList
			[ s6 Variable:/:s6 1 ];
	}
	
	Process ExpressionFluxProcess( re71 )
	{
		Name	"-> [s7]; { s3 };";
		k71	-10.0;
		km71	5.0;
		ki71	1.0;
		Expression	"s7.NumberConc * k71 / (s7.NumberConc + km71) / (1 + s3.NumberConc / ki71)";
		VariableReferenceList
			[ s7 Variable:/:s7 1 ]
			[ s3 Variable:/:s3 0 ];
	}
	
	Process ExpressionFluxProcess( re72 )
	{
		Name	"-> [s7]; { s6 };";
		k72	1.0;
		km72	5.0;
		Expression	"k72 * s6.NumberConc / (km72 + s6.NumberConc)";
		VariableReferenceList
			[ s7 Variable:/:s7 1 ]
			[ s6 Variable:/:s6 0 ];
	}
	
	
}

System System( /A )
{
	StepperID	Default;

	Variable Variable( SIZE )
	{
		Value	1.0;
		Fixed	1;
	}

}
'''
