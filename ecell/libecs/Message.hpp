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

#ifndef ___MESSAGE_H___
#define ___MESSAGE_H___
#include <string>
#include <map>
#include <vector>
#include "Exceptions.h"
#include "StringList.h"
#include "Defs.h"

DECLARE_CLASS( Message )
DECLARE_CLASS( AbstractMessageSlot )
DECLARE_CLASS( MessageSlot )
DECLARE_CLASS( MessageInterface )

  /**
     A string data packet for communication among C++ objects.

     @see MessageInterface
     @see AbstractMessageSlot
   */
class Message : private StringPair
{

public: // exceptions

  class MessageException : public Exception
    {
    public:
      MessageException(StringCref method,StringCref what)
	: Exception(method,what){}
    };
  class BadMessage : public MessageException
    {
    public:
      BadMessage(StringCref method,StringCref what)
	: MessageException(method,what){}
    };

public:

  Message( StringCref keyword, StringCref body ); 
  Message( StringCref keyword, const Float f );
  Message( StringCref keyword, const Int i );
  Message( StringCref message ); 

  // copy procedures
  Message( MessageCref message );
  Message& operator=( MessageCref );
  
  virtual ~Message();

  /**
    Returns keyword string of this Message.

    @return keyword string.
    @see body()
   */
  StringCref getKeyword() const { return first; }

  /**
    Returns body string of this Message.

    @return body string.
    @see keyword()
   */
  StringCref getBody() const { return second; }

  /**
    Returns nth field of body string using FIELD_SEPARATOR as delimiter.  

    @return nth field of body string.
    @see FIELD_SEPARATOR
   */
  const String getBody( int n ) const;


  const String dump() const { return first + ' ' + second; }

};


/**
   A base class for MessageCallback class.

   @see MessageCallback
   @see MessageInterface
   @see Message
 */
class AbstractMessageCallback
{

public:

  // exceptions

  class CallbackFailed : public Message::MessageException
    {
    public: 
      CallbackFailed( StringCref method, StringCref message )
	: MessageException( method, message ) {}
      const String what() const { return "Callback has failed."; }
    };

  class NoMethod : public Message::MessageException
    {
    public: 
      NoMethod( StringCref method, StringCref what )
	: MessageException( method, what ) {}
      const String what() const { return "No method registered for the slot"; }
    };

  virtual void set( MessageCref message ) = 0;
  virtual const Message get( StringCref keyword ) = 0;

  virtual void operator()( MessageCref message ) 
    { set( message ); }
  virtual const Message operator()( StringCref keyword ) 
    { return get(keyword); }
};


/**
   Calls callback methods for getting and sending Message objects.

   @see Message
   @see MessageInterface
   @see AbstractMessageCallback
 */
template <class T>
class MessageCallback : public AbstractMessageCallback
{

public:

  typedef void ( T::* SetMessageFunc )( MessageCref );
  typedef const Message ( T::* GetMessageFunc )( StringCref );

public:

  MessageCallback( T& object, const SetMessageFunc setmethod,
		   const GetMessageFunc getmethod )
    : 
    theObject( object ), 
    theSetMethod( setmethod ), 
    theGetMethod( getmethod ) 
    {
      ; // do nothing
    }
  
  virtual void set( MessageCref message ) 
    {
      if( theSetMethod == NULLPTR )
	{
	  //FIXME: throw an exception
	  return;
	}
      ( theObject.*theSetMethod )( message );
    }

  virtual const Message get( StringCref keyword ) 
    {
      if( theGetMethod == NULLPTR )
	{
	  //FIXME: throw an exception
	  return Message( keyword, "" );
	}
      return ( ( theObject.*theGetMethod )( keyword ));
    }

private:

  T& theObject;
  const SetMessageFunc theSetMethod;
  const GetMessageFunc theGetMethod;

};



/**
  Common base class for classes which receive Messages.

  NOTE:  Subclasses of MessageInterface MUST call their own makeSlots() 
  to make their slots in their constructors.
  (virtual functions doesn't work in constructors)

  @see Message
  @see MessageCallback
*/
class MessageInterface
{
public:  

  typedef map< const String, AbstractMessageCallback* > SlotMap;
  typedef SlotMap::iterator SlotMapIterator;

  // exceptions

  class NoSuchSlot : public Message::MessageException
    {
    public: 
      NoSuchSlot( StringCref method, StringCref what )
	: MessageException( method, what ){}
      const String what() const { return "No appropriate slot found"; }
    };

public:

  MessageInterface();

  virtual ~MessageInterface();

  void set( MessageCref ) throw( NoSuchSlot );
  const Message get( StringCref ) throw( NoSuchSlot );
  StringList slotList();

  virtual void makeSlots() = 0;

  virtual const char* const className() const { return "MessageInterface"; }

protected:

  void appendSlot( StringCref keyword, AbstractMessageCallback* );
  void deleteSlot( StringCref keyword );

private:

  SlotMap theSlotMap;

};


#define MessageSlot( KEY, CLASS, OBJ, SETMETHOD, GETMETHOD )\
appendSlot( KEY, new MessageCallback< CLASS >\
	   ( OBJ, static_cast< MessageCallback< CLASS >::SetMessageFunc >\
	    ( SETMETHOD ),\
	    static_cast< MessageCallback< CLASS >::GetMessageFunc >\
	    ( GETMETHOD ) ) )

#endif /* ___MESSAGE_H___*/


/*
  Do not modify
  $Author$
  $Revision$
  $Date$
  $Locker$
*/
