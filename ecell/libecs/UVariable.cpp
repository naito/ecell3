//::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
//
//        This file is part of E-CELL Simulation Environment package
//
//                Copyright (C) 1996-2001 Keio University
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

#include <typeinfo>

#include "Util.hpp"
#include "Exceptions.hpp"

#include "UVariable.hpp"

namespace libecs
{

  UVariableStringData::UVariableStringData( const Real f )
    :
    theString( toString<Real>( f ) )
  {
    ; // do nothing
  }

  UVariableStringData::UVariableStringData( const Int i )
    :
    theString( toString<Int>( i ) )
  {
    ; // do nothing
  }

  const Real UVariableStringData::asReal() const
  {
    cerr << "R "<< theString << endl;
    return stringTo<Real>( theString );
  }

  const Int UVariableStringData::asInt() const
  {
    return stringTo<Int>( theString );
  }


  UVariableRealData::UVariableRealData( StringCref str )
    :
    theReal( stringTo<Real>( str ) )
  {
    ; // do nothing
  }

  const String UVariableRealData::asString() const
  {
    return toString<Real>( theReal );
  }

  UVariableIntData::UVariableIntData( StringCref str )
    :
    theInt( stringTo<Int>( str ) )
  {
    ; // do nothing
  }

  UVariableIntData::UVariableIntData( const Real f )
    :
    // FIXME: range check?
    theInt( static_cast<Int>( f ) )
  {
    ; // do nothing
  }


  const String UVariableIntData::asString() const
  {
    return toString<Int>( theInt );
  }


  const UVariable::Type UVariable::getType() const
  {
    if( typeid( *theData) == typeid( UVariableRealData ) )
      {
	return REAL;
      }
    else if( typeid( *theData ) == typeid( UVariableIntData ) )
      {
	return INT;
      }
    else if( typeid( *theData ) == typeid( UVariableStringData ) )
      {
	return STRING;
      }
    else if( typeid( *theData ) == typeid( UVariableNoneData ) )
      {
	return NONE;
      }
    
    // NEVER_GET_HERE
    throw UnexpectedError( __PRETTY_FUNCTION__ + String( "NEVER_GET_HERE" ) );
  }


} // namespace libecs
