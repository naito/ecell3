
char const Entity_C_rcsid[] = "$Id$";
//::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
//
// 		This file is part of Serizawa (E-CELL Core System)
//
//	       written by Kouichi Takahashi  <shafi@sfc.keio.ac.jp>
//
//                              E-CELL Project,
//                          Lab. for Bioinformatics,  
//                             Keio University.
//
//             (see http://www.e-cell.org for details about E-CELL)
//
//::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
//
//
// Serizawa is free software; you can redistribute it and/or
// modify it under the terms of the GNU General Public
// License as published by the Free Software Foundation; either
// version 2 of the License, or (at your option) any later version.
// 
// Serizawa is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
// See the GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public
// License along with Serizawa -- see the file COPYING.
// If not, write to the Free Software Foundation, Inc.,
// 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
// 
//END_HEADER




#include "Entity.h"
//FIXME: #include "ecell/MessageWindow.h"
#include "System.h"
#include "FQPN.h"
#include "RootSystem.h"
#include "Stepper.h"


Entity::Entity()
: _supersystem(NULL),_entryname(""),_name("") 
{
  makeSlots();
}


Entity::~Entity()
{
  makeSlots();
}

void Entity::makeSlots()
{
  // empty

}

Float Entity::activity() 
{
//FIXME:   *theMessageWindow << "warning: request for activity from " << className() 
//FIXME:     << " [" << entryname() << "] which have no activity function defined.\n";
  return 0;
}

Float Entity::activityPerSec() 
{
  return (activity()  / supersystem()->stepper()->deltaT());
}

const string Entity::fqen() const
{
  string fqen = systemPath();
  if(fqen != "")
    fqen += ":";
  fqen += entryname();

  return fqen;
}

const string Entity::fqpn() const
{
  return Primitive::PrimitiveTypeString(Primitive::ENTITY) + ":" + fqen();
}

const string Entity::systemPath() const
{
  if(!supersystem())
    return "";

  string systempath = supersystem()->systemPath(); 
  if(systempath != "" && systempath != "/")
    systempath += SystemPath::DELIMITER;      
  systempath += supersystem()->entryname(); 


  return systempath;
}



/*
void Entity::setSupersystem(const string& supersystem)
{
  System* s;
  try {
    s = theRootSystem->name2System(supersystem);
    }
  catch(MetaSystem::CantFindSystem& e)
    {
//FIXME:       *theMessageWindow << __PRETTY_FUNCTION__ << ": " 
//FIXME: 	<< e.message() << "\n";
      return;
    }
  setSupersystem(s);
}
*/
