//::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
//
//        This file is part of E-CELL Simulation Environment package
//
//                Copyright (C) 1996-2002 Keio University
//
//::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
//
//
// E-CELL is free software; you can redistribute it and/or
// modify it under the terms of the GNU General Public
// License as published by the Free Software Foundation; either
// version 2 of the License, or (at your option) any later version.
// 
// E-CELL is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
// See the GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public
// License along with E-CELL -- see the file COPYING.
// If not, write to the Free Software Foundation, Inc.,
// 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
// 
//END_HEADER
//
// written by Kouichi Takahashi <shafi@e-cell.org> at
// E-CELL Project, Lab. for Bioinformatics, Keio University.
//

#include <functional>
#include <algorithm>
#include <limits>

#include "Substance.hpp"
#include "Reactor.hpp"
#include "FullID.hpp"
#include "PropertySlotMaker.hpp"

// to be removed (for SRM)
#include "Integrators.hpp"

#include "Stepper.hpp"


namespace libecs
{


  ////////////////////////// Stepper

  
  void Stepper::makeSlots()
  {

    registerSlot( getPropertySlotMaker()->
		  createPropertySlot( "ID", *this,
				      Type2Type<String>(),
				      NULLPTR,
				      &Stepper::getID ) );

    registerSlot( getPropertySlotMaker()->
		  createPropertySlot( "SystemList", *this,
				      Type2Type<PolymorphVectorRCPtr>(),
				      NULLPTR,
				      &Stepper::getSystemList ) );

    registerSlot( getPropertySlotMaker()->
		  createPropertySlot( "CurrentTime", *this,
				      Type2Type<Real>(),
				      NULLPTR,
				      &Stepper::getCurrentTime ) );

    registerSlot( getPropertySlotMaker()->
		  createPropertySlot( "StepInterval", *this,
				      Type2Type<Real>(),
				      &Stepper::setStepInterval,
				      &Stepper::getStepInterval ) );

    registerSlot( getPropertySlotMaker()->
		  createPropertySlot( "StepsPerSecond", *this,
				      Type2Type<Real>(),
				      NULLPTR,
				      &Stepper::getStepsPerSecond ) );

    registerSlot( getPropertySlotMaker()->
		  createPropertySlot( "MaxInterval", *this,
				      Type2Type<Real>(),
				      &Stepper::setMaxInterval,
				      &Stepper::getMaxInterval ) );

    registerSlot( getPropertySlotMaker()->
		  createPropertySlot( "MinInterval", *this,
				      Type2Type<Real>(),
				      &Stepper::setMinInterval,
				      &Stepper::getMinInterval ) );


  }

  Stepper::Stepper() 
    :
    theCurrentTime( 0.0 ),
    theStepInterval( 0.001 ),
    theMinInterval( 0.0 ),
    theMaxInterval( std::numeric_limits<Real>::max() ),
    theEntityListChanged( true )
  {
    makeSlots();
    calculateStepsPerSecond();
  }

  void Stepper::initialize()
  {
    FOR_ALL( SystemVector, theSystemVector, initialize );
  }


  const PolymorphVectorRCPtr Stepper::getSystemList() const
  {
    PolymorphVectorRCPtr aVectorPtr( new PolymorphVector );
    aVectorPtr->reserve( theSystemVector.size() );

    for( SystemVectorConstIterator i = getSystemVector().begin() ;
	 i != getSystemVector().end() ; ++i )
      {
	SystemCptr aSystemPtr( *i );
	FullIDCref aFullID( aSystemPtr->getFullID() );
	const String aFullIDString( aFullID.getString() );

	aVectorPtr->push_back( aFullIDString );
      }

    return aVectorPtr;
  }


  void Stepper::registerSystem( SystemPtr aSystem )
  { 
    theSystemVector.push_back( aSystem );
  }

  void Stepper::removeSystem( SystemPtr aSystem )
  { 
    SystemVectorIterator i( find( theSystemVector.begin(), 
				  theSystemVector.end(),
				  aSystem ) );

    if( i == theSystemVector.end() )
      {
	THROW_EXCEPTION( NotFound,
			 getClassName() + String( ": " ) 
			 + getID() + ": " + aSystem->getFullID().getString() 
			 + " not found in this stepper." );
      }

    theSystemVector.erase( i );
  }

  void Stepper::registerPropertySlotWithProxy( PropertySlotPtr aSlotPtr )
  {
    if( std::find( thePropertySlotWithProxyVector.begin(),
		   thePropertySlotWithProxyVector.end(), aSlotPtr ) == 
	thePropertySlotWithProxyVector.end() )
      {
	thePropertySlotWithProxyVector.push_back( aSlotPtr );
      }
  }

  void Stepper::registerLoggedPropertySlot( PropertySlotPtr aPropertySlotPtr )
  {
    theLoggedPropertySlotVector.push_back( aPropertySlotPtr );
  }

  void Stepper::setStepInterval( RealCref aStepInterval )
  {
    theStepInterval = aStepInterval;
    calculateStepsPerSecond();
  }

  void Stepper::calculateStepsPerSecond() 
  {
    theStepsPerSecond = 1.0 / getStepInterval();
  }

  void Stepper::sync()
  {
    FOR_ALL( PropertySlotVector, thePropertySlotWithProxyVector, sync );
  }

  void Stepper::push()
  {
    FOR_ALL( PropertySlotVector, thePropertySlotWithProxyVector, push );

    // update loggers
    FOR_ALL( PropertySlotVector, theLoggedPropertySlotVector, updateLogger );
  }


  ////////////////////////// SRMStepper

  SRMStepper::SRMStepper()
    :
    theIntegratorAllocator( NULLPTR )
  {
    ; // do nothing
  }

  void SRMStepper::clear()
  {
    //
    // Substance::clear()
    //
    FOR_ALL( SRMSubstanceCache, theSubstanceCache, clear );

    //
    // Reactor::clear() ?
    //
    //FOR_ALL( ,, clear );

    //
    // System::clear() ?
    //
    //FOR_ALL( ,, clear );
  }



  void SRMStepper::react()
  {
    //
    // Reactor::react()
    //
    FOR_ALL( ReactorVector, theReactorCache, react );

    //
    // Substance::turn()
    //
    FOR_ALL( SRMSubstanceCache, theSubstanceCache, turn );    
  }


  void SRMStepper::integrate()
  {
    //
    // Reactor::integrate()
    //
    FOR_ALL( ReactorVector, theReactorCache, integrate );

    //
    // Substance::integrate()
    //
    FOR_ALL( SRMSubstanceCache, theSubstanceCache, integrate );

    //
    // System::integrate()
    //
    FOR_ALL( SystemVector, theSystemVector, integrate );

  }


  void SRMStepper::initialize()
  {
    Stepper::initialize();

    if( isEntityListChanged() )
      {
	theSubstanceCache.update( theSystemVector );
	theReactorCache.update( theSystemVector );

	clearEntityListChanged();
      }

    distributeIntegrator( theIntegratorAllocator );
  }

  void SRMStepper::distributeIntegrator( Integrator::AllocatorFuncPtr
					 anAllocator )
  {
    for( SRMSubstanceCache::const_iterator s( theSubstanceCache.begin() );
	 s != theSubstanceCache.end() ; ++s )
      {
	(* anAllocator )(**s);
      }
  }



  ////////////////////////// Euler1SRMStepper

  Euler1SRMStepper::Euler1SRMStepper()
  {
    theIntegratorAllocator = &Euler1SRMStepper::newIntegrator;
  }

  IntegratorPtr Euler1SRMStepper::newIntegrator( SRMSubstanceRef substance )
  {
    return new Euler1Integrator( substance );
  }

  ////////////////////////// RungeKutta4SRMStepper

  RungeKutta4SRMStepper::RungeKutta4SRMStepper()
  {
    theIntegratorAllocator = &RungeKutta4SRMStepper::newIntegrator; 
  }

  IntegratorPtr RungeKutta4SRMStepper::
  newIntegrator( SRMSubstanceRef aSubstance )
  {
    return new RungeKutta4Integrator( aSubstance );
  }

  void RungeKutta4SRMStepper::react()
  {
    SRMStepper::react();
    SRMStepper::react();
    SRMStepper::react();
    SRMStepper::react();
  }

} // namespace libecs


/*
  Do not modify
  $Author$
  $Revision$
  $Date$
  $Locker$
*/
