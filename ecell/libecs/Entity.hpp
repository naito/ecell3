//::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
//
//        This file is part of E-CELL Simulation Environment package
//
//                Copyright (C) 1996-2000 Keio University
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

#ifndef ___ENTITY_H___
#define ___ENTITY_H___
#include <string>
#include "util/Message.h"
#include "Koyurugi.h"

/**
   Entity class is a base class for all components in the cell model.
   Entity is-a MessageInterface. (i.e. It can accept Message objects
   and requests for Messages.)

   It has entryname, name and supersystem as common properties.
*/
class Entity : public MessageInterface
{

public:

  Entity(); 
  virtual ~Entity();

  /**
    Set supersystem pointer of this Entity.  
    Usually no need to set this manually because a System object will 
    do this when an Entity is installed to the System.

    @param supersystem name of a System object to which this object
    belongs.
   */
  virtual void setSupersystem( SystemPtr const supersystem ) 
   { theSupersystem = supersystem; }

  SystemPtr getSupersystem() const {return theSupersystem;}

  /**
    Set an identifier of this Entity.

    @param entryname entryname of this Entry.
   */
  void setId( StringCref id ) { theId = id; }

  /**
    @return entryname of this Entity.
   */
  StringCref getId() const { return theId; }

  /**
    Set name of this Entity.

    @param name name of this Entity.
   */
  void setName( StringCref name ) { theName = name; }

  /**
    @return name of this Entity.
   */
  StringCref getName() const { return theName; }

  /**
    @return SystemPath of this Entity.
   */
  const String getSystemPath() const;

  /**
    @return FQIN (Fully Qualified ?????) of this Entity.
   */
  const String getFqin() const;

  /**
    @return FQPN (Fully Qualified ?????) of this Entity.
   */
  const String getFqpn() const;

  /**
    Returns activity value of this Entity defined in subclasses.
    Thus this should be overrided to calculate and return activity value 
    defined in each derived class. The time width used in this method
    should be delta-T. In case activity per second is needed, use
    getActivityPerSecond() method.

    @return activity of this Entity
    @see getActivityPerSecond()
   */
  virtual Float getActivity();

  /**
    Returns activity value (per second).
    Default action of this method is to return getActivity() / delta-T,
    but this action can be changed in subclasses.

    @return activity of this Entity per second
   */
  virtual Float getActivityPerSecond();

  virtual const char* const getClassName() const { return "Entity"; }

protected:

  virtual void makeSlots();

private:

  // hide them
  Entity( Entity& ) {}
  Entity& operator=( Entity& ) {}

private:

  SystemPtr theSupersystem;
  String theId;
  String theName;
};

#endif /*  ___ENTITY_H___ */

/*
  Do not modify
  $Author$
  $Revision$
  $Date$
  $Locker$
*/
