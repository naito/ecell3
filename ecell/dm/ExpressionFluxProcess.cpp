//::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
//
//        This file is part of E-CELL Simulation Environment package
//
//                Copyright (C) 2003 Keio University
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
// authors:
// Kouichi Takahashi <shafi@e-cell.org>
// Nayuta Iwata
//
// E-CELL Project, Lab. for Bioinformatics, Keio University.
//


#include "ExpressionProcessBase.hpp"

USE_LIBECS;

LIBECS_DM_CLASS( ExpressionFluxProcess, ExpressionProcessBase )
{
 public:
  
  LIBECS_DM_OBJECT( ExpressionFluxProcess, Process )
    {
      INHERIT_PROPERTIES( ExpressionProcessBase );
    }

  ExpressionFluxProcess()
  {
    //FIXME: additional properties:
    // Unidirectional   -> call declareUnidirectional() in initialize()
    //                     if this is set
  }

  virtual ~ExpressionFluxProcess()
  {
    ; // do nothing
  }
  
  
  virtual void process()
    { 
      setFlux( theStackMachine.execute( theCompiledCode ) );
    }

};

LIBECS_DM_INIT( ExpressionFluxProcess, Process );