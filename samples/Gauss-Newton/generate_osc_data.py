# -*- coding: utf-8 -*-

from ecell.ECDDataFile import *
import numpy as np
import os
import json

# --------------------------------------------------------
# parameters for the model
# --------------------------------------------------------

TARGET = [ 
    'Variable:/:s1:Value', 
    'Variable:/:s2:Value', 
    'Variable:/:s3:Value' ]

# --------------------------------------------------------
# EM of the model
# --------------------------------------------------------
EM_NAME = 'simple.em'

EM = '''
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
		Value	0.0;
		Fixed	0;
	}
	
	Variable Variable( s2 )
	{
		Name	s2;
		Value	0.25;
		Fixed	0;
	}
	
	Variable Variable( s3 )
	{
		Name	s3;
		Value	0.0625;
		Fixed	0;
	}
	
	Process ExpressionFluxProcess( re11 )
	{
		Name	"-> [s1]; { s2 };";
		k11	1.0;
		Expression	"k11 * s2.NumberConc";
		VariableReferenceList
			[ s1 Variable:/:s1 1 ]
			[ s2 Variable:/:s2 0 ];
	}
	
	Process ExpressionFluxProcess( re21 )
	{
		Name	"-> [s2]; { s3 };";
		k21	-1.0;
		Expression	"k21 * s2.NumberConc * s3.NumberConc";
		VariableReferenceList
			[ s2 Variable:/:s2 1 ]
			[ s3 Variable:/:s3 0 ];
	}
	
	Process ExpressionFluxProcess( re22 )
	{
		Name	"-> [s2]; { s1 };";
		k22	-1.0;
		Expression	"k22 * s1.NumberConc";
		VariableReferenceList
			[ s2 Variable:/:s2 1 ]
			[ s1 Variable:/:s1 0 ];
	}
	
	Process ExpressionFluxProcess( re23 )
	{
		Name	"-> [s2];";
		k23	1.0;
		Expression	"k23 * s2.NumberConc";
		VariableReferenceList
			[ s2 Variable:/:s2 1 ];
	}
	
	Process ExpressionFluxProcess( re31 )
	{
		Name	"-> [s3];";
		k31	-1.0;
		Expression	"k31 * s3.NumberConc";
		VariableReferenceList
			[ s3 Variable:/:s3 1 ];
	}
	
	Process ExpressionFluxProcess( re32 )
	{
		Name	"-> [s3]; { s1 };";
		k32	1.0;
		Expression	"k32 * s1.NumberConc * s1.NumberConc";
		VariableReferenceList
			[ s3 Variable:/:s3 1 ]
			[ s1 Variable:/:s1 0 ];
	}
	
	
}
'''


# --------------------------------------------------------
# (1) load model
# --------------------------------------------------------
setModel( EM, EM_NAME )


# --------------------------------------------------------
# (3) create logger stubs
# --------------------------------------------------------
logger_dict = {}

for a_target_FullPN in TARGET:
    logger_dict[ a_target_FullPN ] = createLoggerStub( a_target_FullPN )
    logger_dict[ a_target_FullPN ].create()


# --------------------------------------------------------
# (4) run
# --------------------------------------------------------

run( 11.0 )
step( 1 )


# --------------------------------------------------------
# (6) save predicted time-course
# --------------------------------------------------------
aPredictedTimeCouseList = []

for a_FullPN, a_Logger in logger_dict.items():

    a_time_course = ECDDataFile( a_Logger.getData( 0, 11, 0.01 ) )
    a_time_course.setDataName( a_Logger.getName() )
    a_time_course.setNote( 'Predicted {}'.format( a_FullPN ) )
    a_time_course.save( '{}.ecd'.format( a_FullPN.split(':')[2] ) )


# end of this file
