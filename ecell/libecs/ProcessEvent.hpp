//::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
//
//        This file is part of E-Cell Simulation Environment package
//
//                Copyright (C) 1996-2005 Keio University
//                Copyright (C) 2005 The Molecular Sciences Institute
//
//::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
//
//
// E-Cell is free software; you can redistribute it and/or
// modify it under the terms of the GNU General Public
// License as published by the Free Software Foundation; either
// version 2 of the License, or (at your option) any later version.
// 
// E-Cell is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
// See the GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public
// License along with E-Cell -- see the file COPYING.
// If not, write to the Free Software Foundation, Inc.,
// 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
// 
//END_HEADER
//
// written by Kouichi Takahashi <shafi@e-cell.org>,
// E-Cell Project, Institute for Advanced Biosciences, Keio University.
//

#ifndef __PROCESSEVENT_HPP
#define __PROCESSEVENT_HPP

#include "libecs.hpp"
#include "Process.hpp"

#include "EventScheduler.hpp"


namespace libecs
{

  /** @file */

  DECLARE_CLASS( ProcessEvent );

  class ProcessEvent
    :
    public EventBase
  {


  public:

    ProcessEvent( TimeParam aTime, ProcessPtr aProcessPtr )
      :
      EventBase( aTime ),
      theProcess( aProcessPtr )
    {
      ; // do nothing
    }

    const ProcessPtr getProcess() const
    {
      return theProcess;
    }


    void fire()
    {
      //FIXME: should be theProcess->fire();
      theProcess->addValue( 1.0 );

      reschedule( getTime() );
    }

    void update( TimeParam aTime )
    {
      reschedule( aTime );
    }

    void reschedule( TimeParam aTime )
    {
      const Time aNewStepInterval( theProcess->getStepInterval() );
      setTime( aNewStepInterval + aTime );
    }

    const bool isDependentOn( ProcessEventCref anEvent ) const
    {
      return theProcess->isDependentOn( anEvent.getProcess() );
    }


    const bool operator< ( ProcessEventCref rhs ) const
    {
      // return theTime < rhs.theTime;

      if( getTime() > rhs.getTime() )
	{
	  return false;
	}
      else if( getTime() < rhs.getTime() )
	{
	  return true;
	}
      else // if theTime == rhs.theTime,
	{  // then higher priority comes first.  
	  if( theProcess->getPriority() < rhs.getProcess()->getPriority() )
	    {
	      return true;
	    }
	  else
	    {
	      return false;
	    }
	}
    }

    const bool operator!= ( ProcessEventCref rhs ) const
    {
      if( getTime() == rhs.getTime() && 
	  getProcess() == rhs.getProcess() )
	{
	  return false;
	}
      else
	{
	  return true;
	}
    }


    // dummy, because DynamicPriorityQueue requires this. better without.
    ProcessEvent()
    {
      ; // do nothing
    }


  private:

    ProcessPtr theProcess;

  };

  /*@}*/

} // namespace libecs




#endif /* __PROCESSEVENT_HPP */




/*
  Do not modify
  $Author$
  $Revision$
  $Date$
  $Locker$
*/
