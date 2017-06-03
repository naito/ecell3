# -*- coding: utf-8 -*-

from ecell.ECDDataFile import *
import numpy as np
import os


# --------------------------------------------------------
# parameters for the model
# --------------------------------------------------------

# When you debug this file, delete forehand # of the following
# parameters and execute,
# [%] ecell3-session session.py

"""
PARAMETERS = { 
    'Process:/:E:KmS' : 0.2, 
    'Process:/:E:KcF' : 1.0 }
TRAINING_DATA_DIR = 'Data'
TRAINING_DATA_DICT = {
    'Variable:/:S:Value' : 'S.ecd',
    'Variable:/:P:Value' : 'P.ecd' }
"""

# --------------------------------------------------------
# EM of the model
# --------------------------------------------------------
EM = '''
Stepper ODE45Stepper( ODE  )
{
    # no property
}

System System( / )
{
    StepperID    ODE;

    Variable Variable( SIZE )
    {
        Value    1e-18;
    }

    Variable Variable( S )
    {
        Value    80000;
    }
    
    Variable Variable( P )
    {
        Value    20000;
    }
    
    Variable Variable( E )
    {
        Value    5000;
    }
    
    Process MichaelisUniUniFluxProcess( E )
    {
        VariableReferenceList
            [ S0 :.:S -1 ]
            [ P0 :.:P 1 ]
            [ C0 :.:E 0 ];
        KmS    1;
        KcF    10;
    }
}
'''


# --------------------------------------------------------
# parameters for the script
# --------------------------------------------------------

# simulation
DULATION = 1000
START_TIME = 0
INTERVAL = 10

# evaluation
MINIMUM_DENOMINATOR = 0.001

# output data
PREFIX_OF_PREDICTED_TIMECOURSE = 'pre'


# --------------------------------------------------------
# (1) load eml file
# --------------------------------------------------------
setModel( EM, 'simple.em' )


# --------------------------------------------------------
# (2) read training time-course
# --------------------------------------------------------
TRAINING_TIME_COURSE_DATA_DICT = {}

for FullPN, ECDFileName in TRAINING_DATA_DICT.items():
    aTimeCouse = ECDDataFile()
    aTimeCouse.load( os.sep.join(( TRAINING_DATA_DIR.rstrip( os.sep ), ECDFileName )) )
    TRAINING_TIME_COURSE_DATA_DICT[ FullPN ] = dict( ECDFileName = ECDFileName, ECDData = aTimeCouse )


# --------------------------------------------------------
# (3) set parameter
# --------------------------------------------------------
EntityStubDict = {}
for FullPN, value in PARAMETERS.items():
    PN = FullPN.split(':')[ -1 ]
    FullID = FullPN[ : len( FullPN ) - len( PN ) - 1 ]
    if FullID not in EntityStubDict:
        EntityStubDict[ FullID ] = createEntityStub( FullID )
    EntityStubDict[ FullID ].setProperty( PN, value )

# --------------------------------------------------------
# (4) create logger stubs
# --------------------------------------------------------
aLoggerDict = {}

for FullPN in TRAINING_TIME_COURSE_DATA_DICT.keys():

    aLogger = createLoggerStub( FullPN )
    aLogger.create()
    aLoggerDict[ FullPN ] = aLogger


# --------------------------------------------------------
# (5) run
# --------------------------------------------------------
run( DULATION + INTERVAL )
step( 1 )


# --------------------------------------------------------
# (6) save predicted time-course
# --------------------------------------------------------
predictedTimeCouseDict = {}

for FullPN in TRAINING_TIME_COURSE_DATA_DICT.keys():
    
    aTimeCouse = ECDDataFile( aLoggerDict[ FullPN ].getData(
                              START_TIME, DULATION + INTERVAL, INTERVAL) )
    aTimeCouse.setDataName( aLoggerDict[ FullPN ].getName() )
    aTimeCouse.setNote( 'Predicted {}'.format( FullPN ) )
    aTimeCouse.save( PREFIX_OF_PREDICTED_TIMECOURSE + \
             TRAINING_TIME_COURSE_DATA_DICT[ FullPN ]['ECDFileName'] )

    predictedTimeCouseDict[ FullPN ] = aTimeCouse


# --------------------------------------------------------
# (7) calculate the difference between the training and 
#     the prediction simulated time-course.
# --------------------------------------------------------
aDifference = 0.0
data_size = None

for FullPN in TRAINING_TIME_COURSE_DATA_DICT.keys():

    if data_size == None:
        data_size = TRAINING_TIME_COURSE_DATA_DICT[ FullPN ]['ECDData'].getSize()[ 1 ]

    for t, p in zip( TRAINING_TIME_COURSE_DATA_DICT[ FullPN ]['ECDData'].getData()[ :, 1 ], 
                     np.array( predictedTimeCouseDict[ FullPN ].getData())[ :, 1 ] ):
        # denominator
        if t < MINIMUM_DENOMINATOR:
            aDenominator = MINIMUM_DENOMINATOR
        else:
            aDenominator = t
        # print "t : p = {0:<10} : {0:<10}".format( t, p )
        # add the difference of predicted S and predicted S
        aDifference += pow( ( t - p ) / aDenominator, 2.0 )

aDifference /= data_size

# --------------------------------------------------------
# (8) output the value of fitness function
# --------------------------------------------------------
#open('result.dat','w').write(str(aDifference))
print aDifference

# end of this file
