# -*- coding: utf-8 -*-

import sys

# --------------------------------------------------------
# EM of the model
# --------------------------------------------------------
import Arkin95_model as model


# --------------------------------------------------------
# parameters for the script
# --------------------------------------------------------

ODESteppers = ['FixedODE1Stepper','ODE23Stepper','ODE45Stepper','ODEStepper']

# when rate velocities (Velocity/Value) of all Variables get 
# less than THRESHOLD, the status is identified as a steady 
# state.
THRESHOLD = 1e-6
MAX_TIME  = 1e+8


# --------------------------------------------------------
# functions
# --------------------------------------------------------

def assembleSystemPath( parent, child ):
    parent = parent.strip('/')
    child  = child.strip('/')
    sp = ['',]
    if len( parent ):
        sp.extend( parent.split('/') )
    sp.append( child )
    return '/'.join( sp )

def getRateVelocities( VariableDict ):
    # VariableDict[ FullID ] = VariableStub
    rateVelocities = {}
    for FullID, Stub in VariableDict.items():
        theRateVelocities[ FullID ] = float( Stub.getProperty('Velocity')) / float( Stub.getProperty('Value'))
    return rateVelocities

def isSteady( VariableDict, threshold ):
    for FullID, Stub in VariableDict.items():
        if abs( float( Stub.getProperty('Velocity')) / float( Stub.getProperty('Value'))) > threshold:
            return False
    return True


# --------------------------------------------------------
# (1) load eml file
# --------------------------------------------------------
setModel( model.em, model.name )


# --------------------------------------------------------
# (2) make Variable list
# --------------------------------------------------------
theStepperDict = {}
for Sid in getStepperList():
     theStepperDict[ Sid ] = createStepperStub( Sid )

theVariableList = []
for aStepperID, aStepper in theStepperDict.items():
    if aStepper.getClassname() in ODESteppers:
        theVariableList.extend( aStepper.getProperty('WriteVariableList') )
theVariableList = list( set( theVariableList ) )

theTargetVariableDict = {}
for FullID in theVariableList:
    aVariableStub = createEntityStub( FullID )
    if not aVariableStub.getProperty('Fixed'):
        theTargetVariableDict[ FullID ] = aVariableStub

for FullID, Stub in theTargetVariableDict.items():
    print '{} : Fixed={}'.format( FullID, Stub.getProperty('Fixed') )

if isSteady( theTargetVariableDict, THRESHOLD ):
    print 'Initial condition is already a steady state.'
    sys.exit()

# --------------------------------------------------------
# (3) run
# --------------------------------------------------------
while getCurrentTime() <= MAX_TIME:
    step()
    if isSteady( theTargetVariableDict, THRESHOLD ):
        saveModel( "{}-steady.eml".format( model.name ) )
        print 'The model has arrived at a steady state at t = {}.\nThe steady state is saved as \'{}-steady.eml\'.'.format( getCurrentTime(), model.name )
        sys.exit()

print 'The model has not arrived at a steady state until t = {}.'.format( MAX_TIME )

# end of this file
