//::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
//
//       This file is part of the E-Cell System
//
//       Copyright (C) 1996-2008 Keio University
//       Copyright (C) 2005-2008 The Molecular Sciences Institute
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

#ifndef __MODEL_HPP
#define __MODEL_HPP

#include "dmtool/ModuleMaker.hpp"

#include "libecs/Defs.hpp"
#include "libecs/AssocVector.h"
#include "libecs/EcsObjectMaker.hpp"
#include "libecs/EventScheduler.hpp"
#include "libecs/StepperEvent.hpp"
#include "libecs/LoggerBroker.hpp"
#include "libecs/Stepper.hpp"
#include "libecs/SystemStepper.hpp"
#include "libecs/Handle.hpp"

/**
   @addtogroup model The Model.

   The model.

   @ingroup libecs
   @{ 
*/ 

namespace libecs
{

/**
   Model class represents a simulation model.

   Model has a list of Steppers and a pointer to the root system.
*/
class LIBECS_API Model
{
public:
    DECLARE_ASSOCVECTOR( String, StepperPtr, std::less< const String >,
                         StepperMap ); 
protected:
    typedef EventScheduler< StepperEvent > StepperEventScheduler;
    typedef StepperEventScheduler::EventIndex EventIndex;
    typedef EcsObjectMaker< Stepper > StepperMaker;
    typedef EcsObjectMaker< System > SystemMaker;
    typedef EcsObjectMaker< Variable > VariableMaker;
    typedef EcsObjectMaker< Process > ProcessMaker;
public:
    Model( StaticModuleMaker< EcsObject >& maker );
    ~Model();
    /**
       Initialize the whole model.

       This method must be called before running the model, and when
       structure of the model is changed.

       Procedure of the initialization is as follows:

       1. Initialize Systems recursively starting from theRootSystem.
              ( System::initialize() )
       2. Check if all the Systems have a Stepper each.
       3. Initialize Steppers. ( Stepper::initialize() )
       4. Construct Stepper interdependency graph 
              ( Stepper::updateDependentStepperVector() )


       @throw InitializationFailed
    */
    void initialize();


    /**
       Conduct a step of the simulation.

       @see Scheduler
    */
    void step();


    /**
       Get the next event to occur on the scheduler.
     */
    const StepperEvent& getTopEvent() const
    {
        return theScheduler.getTopEvent();
    }


    /**
       Returns the current time.

       @return time elasped since start of the simulation.
    */
    const Real getCurrentTime() const
    {
        return theCurrentTime;
    }


    const StepperPtr getLastStepper() const
    {
        return theLastStepper;
    }


    /**
       Get the property interface for the specified class.

       @param aClassname
    */
    const PropertyInterfaceBase& getPropertyInterface(
            StringCref aClassname ) const;


    /**
       Creates a new Entity object and register it in an appropriate System
       in the Model.

       @param aClassname
       @param aFullID
       @param aName
    */
    void createEntity( StringCref aClassname, FullIDCref aFullID );


    /**
       Retrieves an Entity object pointed by the FullID.

       @param aFullID a FullID of the requested Entity.
       @return A borrowed pointer to an Entity specified by the FullID.
    */
    Entity* getEntity( FullIDCref aFullID ) const;


    /**
       Retrieves an Entity object by the handle.

       @param handle the handle of the requested Entity.
       @return A borrowed pointer to an Entity specified by the FullID.
    */
    Entity* getEntity( int handle ) const;

    /**
       Retrieves a System object pointed by the SystemPath.    

       @param aSystemPath a SystemPath of the requested System.
       @return A borrowed pointer to a System.
    */
    System* getSystem( SystemPath const& aSystemPath ) const;;


    /**
       Create a stepper with an ID and a classname. 

       @param aClassname  a classname of the Stepper to create.    
       @param anID        a Stepper ID string of the Stepper to create.    
    */
    void createStepper( StringCref aClassname, StringCref anID );


    /**
       Get a stepper by an ID.

       @param anID a Stepper ID string of the Stepper to get.
       @return a borrowed pointer to the Stepper.
    */
    StepperPtr getStepper( StringCref anID ) const;


    /**
       Get the StepperMap of this Model.

       @return the const reference of the StepperMap.
    */
    StepperMapCref getStepperMap() const
    {
        return theStepperMap;
    }


    /**
       Flush the data in all Loggers immediately.

       Usually Loggers record data with logging intervals.    This method
       orders every Logger to write the data immediately ignoring the
       logging interval.
    */
    void flushLoggers();


    /**
       Get the RootSystem.

       @return a borrowed pointer to the RootSystem.
    */
    SystemPtr getRootSystem() const
    {
        return theRootSystemPtr;
    }


    SystemStepperPtr getSystemStepper()
    {
        return &theSystemStepper;
    }

    /**
       Get the LoggerBroker.

       @return a borrowed pointer to the LoggerBroker.
    */
    LoggerBrokerRef getLoggerBroker()
    { 
        return theLoggerBroker; 
    }


    LoggerBrokerCref getLoggerBroker() const
    { 
        return theLoggerBroker; 
    }


    StepperEventScheduler& getScheduler()
    {
        return theScheduler;
    }


    StepperEventScheduler const& getScheduler() const
    {
        return theScheduler;
    }

    void setDMSearchPath( const String& path );

    const String getDMSearchPath() const;

private:
    /// @internal
    void registerBuiltinModules();

    /**
       This method checks recursively if all systems have Steppers
       connected.

       @param aSystem a root node to start recursive search.
       
       @throw InitializationFailed if the check is failed.
    */
    void checkStepper( SystemCptr const aSystem ) const;

    void checkSizeVariable( SystemCptr const aSystem );

    Handle generateNextHandle();

    static void initializeSystems( SystemPtr const aSystem );

public:
    static const char PATH_SEPARATOR = ModuleMaker::PATH_SEPARATOR;

private:

    Time                            theCurrentTime;
    Stepper*                        theLastStepper;

    StepperEventScheduler           theScheduler;

    LoggerBroker                    theLoggerBroker;

    std::map< Handle, EcsObject* >  theObjectMap;
    unsigned int                    theNextHandleVal;

    System*                         theRootSystemPtr;

    std::vector< Entity* >          theDeletionQueue;

    SystemStepper                   theSystemStepper;

    StepperMap                      theStepperMap;

    StaticModuleMaker< EcsObject >& theEcsObjectMaker;
    StepperMaker                    theStepperMaker;
    SystemMaker                     theSystemMaker;
    VariableMaker                   theVariableMaker;
    ProcessMaker                    theProcessMaker;
};

} // namespace libecs

/*@}*/


#endif /* __MODEL_HPP */
