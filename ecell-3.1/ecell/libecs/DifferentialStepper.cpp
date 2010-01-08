//::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
//
//       This file is part of the E-Cell System
//
//       Copyright (C) 1996-2010 Keio University
//       Copyright (C) 2005-2009 The Molecular Sciences Institute
//
//::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
//
//
// E-Cell System is free software; you can redistribute it and/or
// modify it under the terms of the GNU General Public
// License as published by the Free Software Foundation; either
// version 2 of the License, or (at your option) any later version.
// 
// E-Cell System is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
// See the GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public
// License along with E-Cell System -- see the file COPYING.
// If not, write to the Free Software Foundation, Inc.,
// 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
// 
//END_HEADER
//
// written by Koichi Takahashi <shafi@e-cell.org>,
// E-Cell Project.
//
#ifdef HAVE_CONFIG_H
#include "ecell_config.h"
#endif /* HAVE_CONFIG_H */

#include "libecs.hpp"

#include <limits>

#include "Util.hpp"
#include "Variable.hpp"
#include "Interpolant.hpp"
#include "Process.hpp"
#include "Model.hpp"

#include "DifferentialStepper.hpp"

#include <boost/array.hpp>


namespace libecs
{

  LIBECS_DM_INIT_STATIC( DifferentialStepper, Stepper );
  LIBECS_DM_INIT_STATIC( AdaptiveDifferentialStepper, Stepper );

  DifferentialStepper::DifferentialStepper()
    :
    theStateFlag( true ),
    isInterrupted( true ),
    theNextStepInterval( 0.001 ),
    theTolerableStepInterval( 0.001 )
  {
    ; // do nothing
  }

  DifferentialStepper::~DifferentialStepper()
  {
    ; // do nothing
  }

  void DifferentialStepper::initialize()
  {
    Stepper::initialize();

    isInterrupted = true;

    createInterpolants();

    theTaylorSeries.resize( boost::extents[ getStage() ][
            static_cast< RealMatrix::index >(
                getReadOnlyVariableOffset() ) ] );

    // should registerProcess be overrided?
    if ( getDiscreteProcessOffset() < theProcessVector.size() )
      {
	for ( ProcessVectorConstIterator
		i( theProcessVector.begin() + getDiscreteProcessOffset() );
	      i < theProcessVector.end(); ++i )
	  {
	    // XXX: To be addressed later.
	    // std::cerr << "WARNING: Process [" << (*i)->getID() << "] is not continuous." << std::endl;
	  }
      }

    initializeVariableReferenceList();

    // should create another method for property slot ?
    //    setNextStepInterval( getStepInterval() );

    //    theStateFlag = false;
  }

  void DifferentialStepper::initializeVariableReferenceList()
  {
    const ProcessVector::size_type 
      aDiscreteProcessOffset( getDiscreteProcessOffset() );

    theVariableReferenceListVector.clear();
    theVariableReferenceListVector.resize( aDiscreteProcessOffset );
    
    for ( ProcessVector::size_type i( 0 ); i < aDiscreteProcessOffset; ++i )
      {
	ProcessPtr const aProcess( theProcessVector[ i ] );

	VariableReferenceVectorCref aVariableReferenceVector(
	    aProcess->getVariableReferenceVector() );

	VariableReferenceVector::size_type const 
	    aZeroVariableReferenceOffset(
		aProcess->getZeroVariableReferenceOffset() );
	VariableReferenceVector::size_type const 
	    aPositiveVariableReferenceOffset(
		aProcess->getPositiveVariableReferenceOffset() );

	theVariableReferenceListVector[ i ].reserve(
	    ( aVariableReferenceVector.size() - 
		aPositiveVariableReferenceOffset + 
		aZeroVariableReferenceOffset ) );

	for ( VariableReferenceVectorConstIterator 
		anIterator( aVariableReferenceVector.begin() ),
		anEnd ( aVariableReferenceVector.begin() +
		       aZeroVariableReferenceOffset );
	      anIterator < anEnd; ++anIterator )
	  {
	    VariableReference const& aVariableReference( *anIterator );

	    theVariableReferenceListVector[ i ].push_back(
		ExprComponent( getVariableIndex(
			           aVariableReference.getVariable() ),
                               aVariableReference.getCoefficient() ) );
	  }

	for ( VariableReferenceVectorConstIterator anIterator(
		aVariableReferenceVector.begin() +
	        aPositiveVariableReferenceOffset ); 
	      anIterator < aVariableReferenceVector.end(); 
	      ++anIterator )
	  {
	    VariableReference const& aVariableReference( *anIterator );

	    theVariableReferenceListVector[ i ].push_back(
		ExprComponent( getVariableIndex(
			           aVariableReference.getVariable() ),
                               aVariableReference.getCoefficient() ) );
	  }
      }
  }

  void DifferentialStepper::
  setVariableVelocity( boost::detail::multi_array::sub_array<Real, 1>
		       aVelocityBuffer )
  {
    const ProcessVector::size_type 
      aDiscreteProcessOffset( getDiscreteProcessOffset() );

    for ( RealMatrix::index i( 0 );
	  i < static_cast< RealMatrix::index >( aVelocityBuffer.size() );
	  ++i )
      {
	aVelocityBuffer[ i ] = 0.0;
      }

    for ( ProcessVector::size_type i( 0 ); i < aDiscreteProcessOffset; ++i )
      {
	const Real anActivity( theProcessVector[ i ]->getActivity() );

	for ( VariableReferenceList::const_iterator 
		anIterator( theVariableReferenceListVector[ i ].begin() );
	      anIterator < theVariableReferenceListVector[ i ].end();
	      anIterator++ )
	  {
	    ExprComponent const& aComponent = *anIterator;
	    const RealMatrix::index anIndex(
		static_cast< RealMatrix::index >(
		    aComponent.first ) );
	    aVelocityBuffer[ anIndex ] += aComponent.second * anActivity;
	  }
      }
  }

  void DifferentialStepper::reset()
  {
    // is this needed?
    for ( RealMatrix::index i( 0 ); i != getStage(); ++i )
      for ( RealMatrix::index j( 0 );
	    j != getReadOnlyVariableOffset(); ++j )
      {
	theTaylorSeries[ i ][ j ] = 0.0;

	//	RealMatrix::index_gen indices;
	//	theTaylorSeries[ indices[ i ][ RealMatrix::index_range( 0, getReadOnlyVariableOffset() ) ] ].assign( 0.0 );
      }

    Stepper::reset();
  }

  void DifferentialStepper::resetAll()
  {
    const VariableVector::size_type aSize( theVariableVector.size() );
    for ( VariableVector::size_type c( 0 ); c < aSize; ++c )
      {
	VariablePtr const aVariable( theVariableVector[ c ] );
	aVariable->loadValue( theValueBuffer[ c ] );
      }
  }

  void DifferentialStepper::interIntegrate()
  {
    Real const aCurrentTime( getCurrentTime() );

    VariableVector::size_type c( theReadWriteVariableOffset );
    for( ; c != theReadOnlyVariableOffset; ++c )
      {
      	VariablePtr const aVariable( theVariableVector[ c ] );

	aVariable->interIntegrate( aCurrentTime );
      }

    // RealOnly Variables must be reset by the values in theValueBuffer
    // before interIntegrate().
    for( ; c != theVariableVector.size(); ++c )
      {
	VariablePtr const aVariable( theVariableVector[ c ] );

	aVariable->loadValue( theValueBuffer[ c ] );
	aVariable->interIntegrate( aCurrentTime );
      }
  }

  void DifferentialStepper::interrupt( TimeParam aTime )
  {
    const Real aCallerCurrentTime( aTime );

    const Real aCallerTimeScale( getModel()->getLastStepper()->getTimeScale() );
    const Real aStepInterval( getStepInterval() );

    // If the step size of this is less than caller's timescale,
    // ignore this interruption.
    if( aCallerTimeScale >= aStepInterval )
      {
	return;
      }

    // aCallerTimeScale == 0 implies need for immediate reset
    if( aCallerTimeScale != 0.0 )
      {
	// Shrink the next step size to that of caller's
	setNextStepInterval( aCallerTimeScale );

	const Real aNextStep( getCurrentTime() + aStepInterval );
	const Real aCallerNextStep( aCallerCurrentTime + aCallerTimeScale );

	// If the next step of this occurs *before* the next step 
	// of the caller, just shrink step size of this Stepper.
	if( aNextStep <= aCallerNextStep )
	  {
	    return;
	  }
      }
      
    theNextTime = aCallerCurrentTime;
    isInterrupted = true;
  }
 
  void DifferentialStepper::step()
  {
    updateInternalState( getNextStepInterval() );
  }

  void DifferentialStepper::updateInternalState( Real aStepInterval )
  {
    setStepInterval( aStepInterval );
    // check if the step interval was changed, by epsilon
    if ( std::fabs( getTolerableStepInterval() - aStepInterval )
	 > std::numeric_limits<Real>::epsilon() )
      {
	isInterrupted = true;
      }
    else
      {
	isInterrupted = false;
      }
  }


  ////////////////////////// AdaptiveDifferentialStepper

  AdaptiveDifferentialStepper::AdaptiveDifferentialStepper()
    :
    safety( 0.9 ),
    theTolerance( 1.0e-6 ),
    theAbsoluteToleranceFactor( 1.0 ),
    theStateToleranceFactor( 1.0 ),
    theDerivativeToleranceFactor( 1.0 ),
    theEpsilonChecked( 0 ),
    theAbsoluteEpsilon( 0.1 ),
    theRelativeEpsilon( 0.1 ),
    theMaxErrorRatio( 1.0 ),
    theTolerableRejectedStepCount( std::numeric_limits< Integer >::max() )
  {
    // use more narrow range
    theMinStepInterval = 1e-100;
    theMaxStepInterval = 1e+10;
  }

  AdaptiveDifferentialStepper::~AdaptiveDifferentialStepper()
  {
    ; // do nothing
  }


  void AdaptiveDifferentialStepper::initialize()
  {
    DifferentialStepper::initialize();

    //FIXME:!!
    //    theEpsilonChecked = ( theEpsilonChecked 
    //			  || ( theDependentStepperVector.size() > 1 ) );
  }

  void AdaptiveDifferentialStepper::updateInternalState( Real aStepInterval )
  {
    theStateFlag = false;

    clearVariables();

    Integer theRejectedStepCounter( 0 );
    const Real maxError( getMaxErrorRatio() );

    while ( !calculate( aStepInterval ) )
      {
	if ( ++theRejectedStepCounter >= theTolerableRejectedStepCount )
	  {
	    THROW_EXCEPTION( SimulationError,
			     String( "The times of rejections of step "
				     "calculation exceeded a maximum tolerable "
				     "count (" )
			     + stringCast( theTolerableRejectedStepCount )
			     + ")." );
	  }

	// shrink it if the error exceeds 110%
	aStepInterval = aStepInterval * safety * std::pow( getMaxErrorRatio(),
						  -1.0 / getOrder() );
      }

    // an extra calculation for resetting the activities of processes
    fireProcesses();

    setTolerableStepInterval( aStepInterval );

    theStateFlag = true;

    // grow it if error is 50% less than desired
    Real aNewStepInterval( aStepInterval );
    if ( maxError < 0.5 )
      {
	aNewStepInterval = aNewStepInterval * safety * std::pow( maxError,
					    -1.0 / ( getOrder() + 1 ) );
      }
    setNextStepInterval( aNewStepInterval );

    DifferentialStepper::updateInternalState( aStepInterval );
  }

} // namespace libecs


/*
  Do not modify
  $Author$
  $Revision$
  $Date$
  $Locker$
*/