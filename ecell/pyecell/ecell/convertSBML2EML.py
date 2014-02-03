#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#
#       This file is part of the E-Cell System
#
#       Copyright (C) 1996-2012 Keio University
#       Copyright (C) 2005-2009 The Molecular Sciences Institute
#
#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#
#
# E-Cell System is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
# 
# E-Cell System is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public
# License along with E-Cell System -- see the file COPYING.
# If not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
# 
#END_HEADER

import sys
import re
import os
import time
import getopt
import types

from ecell.eml import *
from convertSBMLFunctions import *
import libsbml


def convertSBML2EML( aSBMLString ):

    aSBMLDocument = libsbml.readSBMLFromString( aSBMLString )

    # ------------------------------
    #  Function Definition Converter
    # ------------------------------

    theFunctionDefinitionConverter = libsbml.SBMLFunctionDefinitionConverter()
    theFunctionDefinitionConverter.setDocument( aSBMLDocument )
    print "    FunctionDefinitionConverter: %s" % \
        libsbml.OperationReturnValue_toString( theFunctionDefinitionConverter.convert() )

    # ------------------------------
    #  Initial Assignment Converter
    # ------------------------------

    theInitialAssignmentConverter = libsbml.SBMLInitialAssignmentConverter()
    theInitialAssignmentConverter.setDocument( aSBMLDocument )
    print "    InitialAssignmentConverter:  %s" % \
        libsbml.OperationReturnValue_toString( theInitialAssignmentConverter.convert() )

    ## FIXME: theInitialAssignmentConverter.convert() always returns None.

    
    aSBMLModel = aSBMLDocument.getModel()

    theModel       = SBML_Model( aSBMLDocument, aSBMLModel )
    theCompartment = SBML_Compartment( theModel )
    theParameter   = SBML_Parameter( theModel )
    theSpecies     = SBML_Species( theModel )
    theRule        = SBML_Rule( theModel )
    theReaction    = SBML_Reaction( theModel )
    theEvent       = SBML_Event( theModel )

##    # damp FunctionDefinition
##    print "\n"
##    for aFunctionDefinition in theModel.FunctionDefinitionList:
##        print "FunctionDefinition: %s\n" % str( aFunctionDefinition )


    anEml = Eml()

    # ------------------------------
    #  Set Stepper
    # ------------------------------

##    anEml.createStepper( 'ODEStepper', 'DE' )
##    anEml.createStepper( 'ODE45Stepper', 'DE' )
    anEml.createStepper( 'FixedODE1Stepper', 'DE' )
    anEml.createStepper( 'DiscreteTimeStepper', 'DT' )


    # ------------------------------
    #  Set Compartment ( System )
    # ------------------------------

    # setFullID
    aSystemFullID='System::/'
    anEml.createEntity( 'System', aSystemFullID )
    anEml.setEntityProperty( aSystemFullID, 'StepperID', ['DE'] )
    anEml.setEntityProperty( aSystemFullID, 'Name', ['Default'] )



    for aCompartment in ( theModel.CompartmentList ):

        print "Compartment: " + str( aCompartment )

        # initialize
        theCompartment.initialize( aCompartment )

        # getPath
        if ( theModel.Level == 1 ):
            aPath = theModel.getPath( aCompartment[ 'Name' ] )
        elif ( theModel.Level >= 2 ):
            aPath = theModel.getPath( aCompartment[ 'Id' ] )           
        
        # setFullID
        if( aPath == '/' ):
            aSystemFullID = 'System::/'
        else:
            aSystemFullID = theCompartment.getCompartmentID( aCompartment )
            anEml.createEntity( 'System', aSystemFullID )


            # setStepper 
            anEml.setEntityProperty( aSystemFullID, 'StepperID', ['DE'] )


        # setName( default = [] )
        if ( theModel.Level >= 2 ):
            if ( aCompartment[ 'Name' ] != '' ):
                anEml.setEntityProperty( aSystemFullID,
                                         'Name',
                                         [ aCompartment[ 'Name' ] ] )

        # setDimensions( default = 3 )
        aDimensionsFullID = 'Variable:' + aPath + ':Dimensions'
        anEml.createEntity( 'Variable', aDimensionsFullID )
        aTmpList = [ str( aCompartment[ 'SpatialDimension' ] ) ]
        anEml.setEntityProperty( aDimensionsFullID, 'Value', aTmpList[0:1] )

                  
        # setSIZE
        aSizeFullID = 'Variable:' + aPath + ':SIZE'
        anEml.createEntity( 'Variable', aSizeFullID )

        aSizeValue = theCompartment.getCompartmentSize( aCompartment )
        aSizeUnit = theCompartment.getCompartmentUnit( aCompartment )

        # convert to ECELL Unit
        if ( aSizeUnit != '' ):
            aSizeValue = theModel.convertUnit( aSizeUnit, aSizeValue )

        aTmpList = [ str( aSizeValue ) ]
        anEml.setEntityProperty( aSizeFullID, 'Value', aTmpList[0:1] )


        # setConstant( default = 1 )
        if ( aCompartment[ 'Constant' ] == 1 ):
            anEml.setEntityProperty( aSizeFullID, 'Fixed', ['1',] )
           
           
    # ------------------------------
    #  Set GlobalParameter ( Variable )
    # ------------------------------

    if ( theModel.ParameterList != [] ):
    
        # setGlobalParameterSystem
        aSystemFullID='System:/:SBMLParameter'
        anEml.createEntity( 'System', aSystemFullID )
        anEml.setEntityProperty( aSystemFullID, 'StepperID', ['DE'] )
        anEml.setEntityProperty( aSystemFullID, 'Name', ['Global Parameter'] )


    for aParameter in theModel.ParameterList:

        # setFullID
        aSystemFullID = theParameter.generateFullID( aParameter )
        anEml.createEntity( 'Variable', aSystemFullID )
            
        # setName
        if ( aParameter[ 'Name' ] != '' ):
            anEml.setEntityProperty( aSystemFullID, 'Name', [ aParameter[ 'Name' ] ] )

        # setValue
        aTmpList = [ str( theParameter.getParameterValue( aParameter ) ) ]
        anEml.setEntityProperty( aSystemFullID, 'Value', aTmpList[0:1] )


        # setFixed ( default = 1 )
        if ( aParameter[ 'Constant' ] == 1 ):
            # aTmpList = [ str( aParameter[ 'Constant' ] ) ]
            aTmpList = [ '1' ]
            anEml.setEntityProperty( aSystemFullID, 'Fixed', aTmpList[0:1] )


    # ------------------------------
    #  Set Species ( Variable )
    # ------------------------------

    for aSpecies in theModel.SpeciesList:
        
        print "Species: " + str( aSpecies )
        
        ### setFullID ###
        
        aSystemFullID = theSpecies.generateFullID( aSpecies )
        anEml.createEntity( 'Variable', aSystemFullID )


        ### setName ###
        
        if( theModel.Level >= 2 ):

            if ( aSpecies[ 'Name' ] != '' ):
                anEml.setEntityProperty( aSystemFullID, 'Name', [ aSpecies[ 'Name' ] ] )


        ### setValue ###
        
        aInitialValueDic = theSpecies.getInitialValue( aSpecies )
        anEml.setEntityProperty( 
            aSystemFullID, aInitialValueDic[ 'Property' ],
            [ str( aInitialValueDic[ 'Value' ] ) ] )


        ### setFixed ###

        if ( theSpecies.isConstant( aSpecies )): aFixedValue = "1"
        else: aFixedValue = "0"
        
        anEml.setEntityProperty( aSystemFullID,
                                 'Fixed',
                                 [ aFixedValue ] )


    # ------------------------------
    #  Set Rule ( Process )
    # ------------------------------

    if ( theModel.RuleList != [] ):

        ### make Rule System ###
        
        aSystemFullID='System:/:SBMLRule'
        anEml.createEntity( 'System', aSystemFullID )
        anEml.setEntityProperty( aSystemFullID,
                                 'Name',
                                 ['System for SBML Rule'] )

        anEml.setEntityProperty( aSystemFullID, 'StepperID', ['DE'] )

        
    for aRule in theModel.RuleList:

##        print "Rule: " + str( aRule )

        theRule.initialize()

        ### setFullID ###        
        aSystemFullID = theRule.generateFullID( aRule )


        ### Algebraic Rule ###
        if ( aRule[ 'Type' ] == libsbml.SBML_ALGEBRAIC_RULE ):

            anEml.createEntity( 'ExpressionAlgebraicProcess', aSystemFullID )
            anEml.setEntityProperty( aSystemFullID, 'StepperID', ['DT'] )


        ### Assignment Rule ###
        elif ( aRule[ 'Type' ] == libsbml.SBML_ASSIGNMENT_RULE or
               aRule[ 'Type' ] == libsbml.SBML_SPECIES_CONCENTRATION_RULE or
               aRule[ 'Type' ] == libsbml.SBML_COMPARTMENT_VOLUME_RULE or
               aRule[ 'Type' ] == libsbml.SBML_PARAMETER_RULE ):

            anEml.createEntity( 'ExpressionAssignmentProcess', aSystemFullID )
            anEml.setEntityProperty( aSystemFullID, 'StepperID', ['DT'] )

            if( aRule[ 'Type' ] == libsbml.SBML_ASSIGNMENT_RULE ):
                anEml.setEntityProperty( aSystemFullID, 'Name', [ "Assignment rule for '%s'" % aRule[ 'Variable' ] ] )

            aVariableType = theRule.getVariableType( aRule[ 'Variable' ] )

            if ( aVariableType == libsbml.SBML_SPECIES ):
                theRule.setSpeciesToVariableReference( aRule[ 'Variable' ], '1' )
            elif ( aVariableType == libsbml.SBML_PARAMETER ):
                theRule.setParameterToVariableReference( aRule[ 'Variable' ], '1' )
            elif ( aVariableType == libsbml.SBML_COMPARTMENT ):
                theRule.setCompartmentToVariableReference( aRule[ 'Variable' ], '1' )
            else:
                raise TypeError,\
                    "Variable type must be Species, Parameter, or Compartment"

        ### Rate Rule ###
        elif ( aRule[ 'Type' ] == libsbml.SBML_RATE_RULE ):

            anEml.createEntity( 'ExpressionFluxProcess', aSystemFullID )
            anEml.setEntityProperty( aSystemFullID, 'Name', [ "Rate rule for '%s'" % aRule[ 'Variable' ] ] )

            aVariableType = theRule.getVariableType( aRule[ 'Variable' ] )

            if ( aVariableType == libsbml.SBML_SPECIES ):
                theRule.setSpeciesToVariableReference( aRule[ 'Variable' ], '1' )
            elif ( aVariableType == libsbml.SBML_PARAMETER ):
                theRule.setParameterToVariableReference( aRule[ 'Variable' ], '1' )
            elif ( aVariableType == libsbml.SBML_COMPARTMENT ):
                theRule.setCompartmentToVariableReference( aRule[ 'Variable' ], '1' )
            else:
                raise TypeError,\
                    "Variable type must be Species, Parameter, or Compartment"


        else:
            raise TypeError,\
                " The type of Rule must be Algebraic, Assignment or Rate Rule"

        # convert SBML formula  to E-Cell formula
        convertedFormula = [ str( theRule.convertFormula( aRule[ 'Formula' ] ) ) ]

        # set Expression Property
        anEml.setEntityProperty( aSystemFullID,
                                 'Expression',
                                 convertedFormula )
        
        # setVariableReferenceList
        anEml.setEntityProperty( aSystemFullID,
                                 'VariableReferenceList',
                                 theRule.VariableReferenceList )



    # ------------------------------
    #  Set Reaction ( Process )
    # ------------------------------

    for aReaction in theModel.ReactionList:

##        print "Reaction: " + str( aReaction )

        theReaction.initialize()

        # setFullID
        aSystemFullID = theReaction.generateFullID( aReaction )
        anEml.createEntity( 'ExpressionFluxProcess', aSystemFullID )

        # setName
        if ( theModel.Level >= 2 ):
            if( aReaction[ 'Name' ] != '' ):
                anEml.setEntityProperty( aSystemFullID, 'Name', [ aReaction[ 'Name' ] ] )
            else:
                anEml.setEntityProperty( aSystemFullID, 'Name', [ theReaction.getChemicalEquation( aReaction ) ] )
        else:
            anEml.setEntityProperty( aSystemFullID, 'Name', [ theReaction.getChemicalEquation( aReaction ) ] )

        # setSubstrate
        updateVariableReferenceListBySpeciesList( theModel, theReaction, aReaction[ 'Reactants' ], -1 )
        # setProduct
        updateVariableReferenceListBySpeciesList( theModel, theReaction, aReaction[ 'Products' ] )
        # setCatalyst
        updateVariableReferenceListBySpeciesList( theModel, theReaction, aReaction[ 'Modifiers' ] )


        # setProperty
        if( aReaction[ 'KineticLaw' ] != [] ):
            if( aReaction[ 'KineticLaw' ][4] != [] ):
                for aParameter in aReaction[ 'KineticLaw' ][4]:
                    if ( aParameter[ 'Value' ] != '' ): 
                        aTmpList = [ str( aParameter[ 'Value' ] ) ]
                        if ( theModel.Level == 1 ):
                            anEml.setEntityProperty\
                            ( aSystemFullID, aParameter[ 'Name' ], aTmpList[0:1] )
                        elif ( theModel.Level >= 2 ):
                            anEml.setEntityProperty\
                            ( aSystemFullID, aParameter[ 'Id' ], aTmpList[0:1] )
                            
                          
            # --------------------------
            # set "Expression" Property
            # --------------------------
        
            # convert SBML format formula to E-Cell format formula
            if( aReaction[ 'KineticLaw' ][0] != '' ):
                anExpression =\
                [ str( theReaction.convertFormula( aReaction[ 'KineticLaw' ][0] ) ) ]



                # set Expression Property for ExpressionFluxProcess
                anEml.setEntityProperty( aSystemFullID,
                                         'Expression',
                                         anExpression )

                # setVariableReferenceList
                anEml.setEntityProperty( aSystemFullID,
                                         'VariableReferenceList',
                                         theReaction.VariableReferenceList )

    # ------------------------------
    #  Set Event ( Process )
    # ------------------------------

    if ( theModel.EventList != [] ):

        ### make Event System ###
        
        aSystemFullID='System:/:SBMLEvent'
        anEml.createEntity( 'System', aSystemFullID )
        anEml.setEntityProperty( aSystemFullID,
                                 'Name',
                                 ['System for SBML Event'] )

        anEml.setEntityProperty( aSystemFullID, 'StepperID', ['DE'] )

    for anEvent in theModel.EventList:

##        print "Event: " + str( anEvent )

        theEvent.initialize()

        ### setFullID ###        
        aSystemFullID = theEvent.generateFullID( anEvent )

        anEml.createEntity( 'ExpressionEventProcess', aSystemFullID )
        anEml.setEntityProperty( aSystemFullID, 'StepperID', [ 'DT' ] )
        anEml.setEntityProperty( aSystemFullID, 'Name', [ str( theEvent.getEventName( anEvent ) ) ] )

        # convert EventAssignment
        
        theEventAssignmentList = []
        for anEventAssignment in anEvent[ 'EventAssignments' ]:
            
            aVariableType = theEvent.getVariableType( anEventAssignment[ 0 ] )

            if   ( aVariableType == libsbml.SBML_SPECIES ):
                theEvent.setSpeciesToVariableReference( anEventAssignment[ 0 ], '1' )
            elif ( aVariableType == libsbml.SBML_PARAMETER ):
                theEvent.setParameterToVariableReference( anEventAssignment[ 0 ], '1' )
            elif ( aVariableType == libsbml.SBML_COMPARTMENT ):
                theEvent.setCompartmentToVariableReference( anEventAssignment[ 0 ], '1' )
            else:
                raise TypeError,\
                    "Variable type must be Species, Parameter, or Compartment"
            
            aConvertedEventAssignment = []
            aConvertedEventAssignment.append( anEventAssignment[ 0 ] )
            aConvertedEventAssignment.append( str( theEvent.convertFormula( anEventAssignment[ 1 ] )))
            theEventAssignmentList.append( aConvertedEventAssignment )

        # convert Trigger
        convertedTrigger = [ str( theEvent.convertFormula( anEvent[ 'Trigger' ] )) ]

        # convert Delay
        if ( anEvent[ 'Delay' ] != '' ):
            convertedDelay = [ str( theEvent.convertFormula( anEvent[ 'Delay' ] )) ]
        else:
            convertedDelay = '0.0'

        # set Expression Property
        anEml.setEntityProperty( aSystemFullID,
                                 'EventAssignmentList',
                                 theEventAssignmentList )
        
        # set Expression Property
        anEml.setEntityProperty( aSystemFullID,
                                 'Trigger',
                                 convertedTrigger )
        
        # set Expression Property
        anEml.setEntityProperty( aSystemFullID,
                                 'Delay',
                                 convertedDelay )
        
        # setVariableReferenceList
        anEml.setEntityProperty( aSystemFullID,
                                 'VariableReferenceList',
                                 theEvent.VariableReferenceList )


    return anEml


def updateVariableReferenceListBySpeciesList( theModel, theReaction, aReactingSpeciesList, theDirection = 1 ):
    for aReactingSpecies in aReactingSpeciesList:
        if isinstance( aReactingSpecies, list ):
            _aReactingSpecies = aReactingSpecies
        elif isinstance( aReactingSpecies, str ):
            _aReactingSpecies = [ aReactingSpecies, 0, 1 ]
        else:
            raise Exception,"DEBUG : Unexpected instance during converting Reaction"
        
        if ( _aReactingSpecies[2] != 1 ):     # ReactantDenominator
            raise Exception,"Stoichiometry Error : E-Cell System can't set a floating Stoichiometry"
        
        aStoichiometryInt = theDirection * theReaction.getStoichiometry( _aReactingSpecies[0], _aReactingSpecies[1] )
        
        aCorrespondingVariableReference = theReaction.getVariableReference( _aReactingSpecies[0] )
        if aCorrespondingVariableReference:
            aCorrespondingVariableReference[ 2 ] = str( int( aCorrespondingVariableReference[ 2 ] ) + aStoichiometryInt )
        
        else:
            aReactingSpeciesList = []
            aReactingSpeciesList.append( _aReactingSpecies[0] )
##            theReaction.SubstrateNumber = theReaction.SubstrateNumber + 1
            aVariableFullID = theModel.getSpeciesReferenceID( _aReactingSpecies[0] )
            if ( aVariableFullID == None ):
                raise NameError,"Species "+ _aReactingSpecies[0] +" not found"

            aReactingSpeciesList.append( 'Variable:' + aVariableFullID )
 
            aReactingSpeciesList.append( str( aStoichiometryInt ) )
            theReaction.VariableReferenceList.append( aReactingSpeciesList )
