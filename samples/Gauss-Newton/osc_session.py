# -*- coding: utf-8 -*-

from ecell.ECDDataFile import *
import numpy as np
import os
import json

# --------------------------------------------------------
# parameters for the model
# --------------------------------------------------------

# When you debug this file, delete forehand # of the following
# parameters and execute,
# [%] ecell3-session session.py

# parameters provided by session manager script
# TARGET   : Dictionary of data points
#              key   : FullPN
#              value : time series
# BETA     : Dictionary of parameters to be estimated.
#              key   : FullPN
#              value : value
# DELTA    : changing rate of delta beta.
# DEL_BETA : list of parameters to be fluctuated.
#            if DEL_BETA == None, all parameters in BETA is changed to caluculate the residual


"""
TARGET = {
    'Variable:/:P:Value' : [
        [   0.0, 20000.0000000 ],
        [ 100.0, 36820.0507812 ],
        [ 200.0, 51088.3164062 ],
        [ 300.0, 61966.3554688 ],
        [ 400.0, 70327.7812500 ],
        [ 500.0, 76793.6562500 ],
        [ 600.0, 81816.3281250 ],
        [ 700.0, 85731.2968750 ],
        [ 800.0, 88790.8593750 ],
        [ 900.0, 91186.7421875 ]],
    'Variable:/:S:Value' : [
        [   0.0, 80000.0000000 ],
        [ 100.0, 63179.9492188 ],
        [ 200.0, 48911.6835938 ],
        [ 300.0, 38033.6445312 ],
        [ 400.0, 29672.2187500 ],
        [ 500.0, 23206.3437500 ],
        [ 600.0, 18183.6738281 ],
        [ 700.0, 14268.7041016 ],
        [ 800.0, 11209.1425781 ],
        [ 900.0, 8813.25878906 ]]
}

BETA = { 
    'Process:/:re11:k11' :  1.0, 
    'Process:/:re21:k21' : -1.0, 
    'Process:/:re32:k32' :  1.0 }

DELTA = 0.0001

DEL_BETA = [
    'Process:/:re11:k11' :  1.0
]
"""

# --------------------------------------------------------
# EM of the model
# --------------------------------------------------------
EM_NAME = 'osc.em'

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
# parameters for the script
# --------------------------------------------------------

start_time = float('inf')
end_time   = float('-inf')

if DEL_BETA == None:
    DEL_BETA = []

for a_time_course in TARGET.values():
    if a_time_course[0][0] < start_time:
        start_time = a_time_course[0][0]
    if a_time_course[-1][0] > end_time:
        end_time = a_time_course[-1][0]


# --------------------------------------------------------
# (1) load model
# --------------------------------------------------------
setModel( EM, EM_NAME )


# --------------------------------------------------------
# (2) set parameter
# --------------------------------------------------------
EntityStubDict = {}
for a_beta_FullPN, value in BETA.items():
    PN = a_beta_FullPN.split(':')[ -1 ]
    a_beta_FullID = a_beta_FullPN[ : len( a_beta_FullPN ) - len( PN ) - 1 ]
    if a_beta_FullID not in EntityStubDict.keys():
        EntityStubDict[ a_beta_FullID ] = createEntityStub( a_beta_FullID )
    if a_beta_FullPN in DEL_BETA:
        EntityStubDict[ a_beta_FullID ].setProperty( PN, value * ( 1.0 + DELTA ) )
    else:
        EntityStubDict[ a_beta_FullID ].setProperty( PN, value )
    
    # print "{} : {}".format( a_beta_FullID, EntityStubDict[ a_beta_FullID ].getProperty( PN ) )


# --------------------------------------------------------
# (3) create logger stubs
# --------------------------------------------------------
logger_dict = {}

for a_target_FullPN in TARGET.keys():
    logger_dict[ a_target_FullPN ] = createLoggerStub( a_target_FullPN )
    logger_dict[ a_target_FullPN ].create()


# --------------------------------------------------------
# (4) run
# --------------------------------------------------------

run( end_time )
step( 1 )


# --------------------------------------------------------
# (5) generate predicted time-course data
# --------------------------------------------------------
predicted_time_couse_dict = {}

# dictionary to be returned via JSON
#   key   : FullPN of a target property
#   value : list [ t, v ]
#             t : time
#             v : predicted value


for a_target_FullPN, a_target_time_course in TARGET.items():
    predicted_time_couse_dict[ a_target_FullPN ] = []
    a_predicted_raw_time_couse = np.array( logger_dict[ a_target_FullPN ].getData() )
    
    # print a_predicted_raw_time_couse[:,0:1]
    
    time_points = a_predicted_raw_time_couse[:,0:1]
    
    for a_target_time_point in a_target_time_course:
        i = np.abs( time_points - a_target_time_point[0] ).argmin()
        # print a_target_time_point
        if ( time_points[ i ][0] > a_target_time_point[0] ) and ( i > 0 ):
            i -= 1
        
        predicted_time_couse_dict[ a_target_FullPN ].append( [ 
            a_target_time_point[0], 
            a_predicted_raw_time_couse[ i ][1] ] )
        if i > 0:
            a_predicted_raw_time_couse = a_predicted_raw_time_couse[ i: ]
            time_points = time_points[ i: ]

#    print a_target_FullPN
#    print TARGET[ a_target_FullPN ]                     # list
#    print predicted_time_couse_dict[ a_target_FullPN ]  # np.array
#    print "\n"


# --------------------------------------------------------
# (6) output the predicted time course data
# --------------------------------------------------------
print json.dumps( predicted_time_couse_dict )

# end of this file
