//::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
//
//        This file is part of E-CELL Simulation Environment package
//
//                Copyright (C) 2002 Keio University
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

#include "Variable.hpp"
#include "Process.hpp"
#include "PropertyInterface.hpp"
#include "ESSYNSStepper.hpp"

LIBECS_DM_INIT( ESSYNSStepper, Stepper );

namespace libecs
{

  void ESSYNSStepper::initialize()
  {
    AdaptiveDifferentialStepper::initialize();
 
    // the number of write variables
    const UnsignedInt aSize( getReadOnlyVariableOffset() );
    theK1.resize( aSize );

    // initialize()

    if( theProcessVector.size() == 1 )
      {
	theESSYNSProcessPtr = DynamicCaster<ESSYNSProcessPtr,ProcessPtr>()( theProcessVector[ 0 ]);
	
	theSystemSize = theESSYNSProcessPtr->getSystemSize();
      }
    else
      {
	THROW_EXCEPTION( InitializationFailed, 
			 "Error:in ESYYNSStepper::initialize() " );
      }

    theTaylorOrder = getOrder();

    theESSYNSMatrix.resize(theSystemSize+1);
    RealVector tmp;
    tmp.resize(theTaylorOrder+1);
    for(Int i( 0 ); i < theSystemSize + 1; i++)
    {
      theESSYNSMatrix[i] = tmp;
    }

    /* for( Int i( 1 ); i < theSystemSize+1; i++)
      {
	std::cout<< (theESSYNSMatrix[i-1])[0] << std::endl;
      }
    */
  }

  bool ESSYNSStepper::calculate()
  {
    const UnsignedInt aSize( getReadOnlyVariableOffset() );

    Real aCurrentTime( getCurrentTime() );
    Real aStepInterval( getStepInterval() );

    // write step() function
  
     theESSYNSMatrix = theESSYNSProcessPtr->getESSYNSMatrix();

    //integrate
    Real aY( 0.0 ); 
    for( Int i( 1 ); i < theSystemSize+1; i++ )
      {
	aY = 0.0;//reset aY 
	for( Int m( 1 ); m <= theTaylorOrder; m++ )
	  {
	    aY += ((theESSYNSMatrix[i-1])[m] *
		   gsl_sf_pow_int( aStepInterval, m ) / gsl_sf_fact( m ));
	  }
	(theESSYNSMatrix[i-1])[0] += aY;
	//std::cout<< (theESSYNSMatrix[i-1])[0] <<std::endl;
      }
    
    //set value
    Int anIndex( 0 );
    for( UnsignedInt c( 0 ); c < aSize; ++c )
      {
	VariablePtr const aVariable( theVariableVector[ c ] );
	
	const Real aVelocity( ( exp( (theESSYNSMatrix[anIndex])[0] ) - ( aVariable->getValue() ) ) / aStepInterval );
		     
	
	theVelocityBuffer[ c ] = aVelocity;
	aVariable->setVelocity( theVelocityBuffer[ c ] );
		     
	anIndex++;

      }

    return true;
  }
 
 
}//namespace libecs 
