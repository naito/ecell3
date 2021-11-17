//::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
//       This file is part of the E-Cell System
//
//       Copyright (C) 1996-2021 Keio University
//       Copyright (C) 2008-2021 RIKEN
//       Copyright (C) 2005-2009 The Molecular Sciences Institute
//
//::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
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
// written by Koichi Takahashi <shafi@e-cell.org> for
// E-Cell Project.
//

#include <iostream>
#include <cstring>
#include <cstdlib>
#include <utility>
#include <cctype>
#include <functional>

#include <boost/bind.hpp>
#include <boost/range/begin.hpp>
#include <boost/range/end.hpp>
#include <boost/range/size.hpp>
#include <boost/range/size_type.hpp>
#include <boost/range/const_iterator.hpp>
#if BOOST_VERSION >= 103200 // for boost-1.32.0 or later.
#   include <boost/numeric/conversion/cast.hpp>
#else // use this instead for boost-1.31 or earlier.
#   include <boost/cast.hpp>
#endif
#include <boost/format.hpp>
#include <boost/format/group.hpp>
#include <boost/optional/optional.hpp>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <numpy/arrayobject.h>
#include <bytesobject.h>
#include <unicodeobject.h>
#include <pycapsule.h>
#include <weakrefobject.h>

#include "dmtool/SharedModuleMakerInterface.hpp"

#include "libecs/Model.hpp"
#include "libecs/libecs.hpp"
#include "libecs/Process.hpp"
#include "libecs/Exceptions.hpp"
#include "libecs/Polymorph.hpp"
#include "libecs/DataPointVector.hpp"
#include "libecs/VariableReference.hpp"

using namespace libecs;
namespace py = pybind11;


static std::string VariableReference___str__( VariableReference const* self )
{
    std::string retval;
    retval += "[";
    retval += self->getName().empty() ? "<anonymous>": self->getName();
    retval += " (#";
    retval += stringCast( self->getSerial() );
    retval += "): ";
    retval += "coefficient=";
    retval += stringCast( self->getCoefficient() );
    retval += ", ";
    retval += "variable=";
    retval += self->getVariable() ? self->getVariable()->asString():
                                    self->getFullID().asString();
    retval += ", ";
    retval += "accessor=";
    retval += ( self->isAccessor() ? "true": "false" );
    retval += "]";
    return retval;
}

class VariableReferences
{
public:
    Process* theProc;
    VariableReferences( Process* proc ): theProc( proc ) {}
    /*
    PyObject* __iter__()
    {
        return STLIteratorWrapper< Process::VariableReferenceVector::const_iterator >::create( theProc->getVariableReferenceVector() );
    }
    */
};

inline const char* typeCodeToString( enum PropertySlotBase::Type aTypeCode )
{
    switch ( aTypeCode )
    {
    case PropertySlotBase::POLYMORPH:
        return "polymorph";
    case PropertySlotBase::REAL:
        return "real";
    case PropertySlotBase::INTEGER:
        return "integer";
    case PropertySlotBase::STRING:
        return "string";
    }
    return "???";
}

class AbstractSimulator: public Model
{
public:
    py::list getStepperList() const
    {
        Model::StepperMap const& aStepperMap( getStepperMap() );
        py::list retval;

        for( Model::StepperMap::const_iterator i( aStepperMap.begin() );
             i != aStepperMap.end(); ++i )
        {
            retval.append( PyUnicode_DecodeLatin1( (*i).first.data(), (*i).first.length(), NULL ) );
        }

        return retval;
    }

    std::vector< String >
    getStepperPropertyList( String const& aStepperID ) const
    {
        return getStepper( aStepperID )->getPropertyList();
    }

    PropertyAttributes
    getStepperPropertyAttributes( String const& aStepperID,
                                  String const& aPropertyName ) const
    {
        return getStepper( aStepperID )->getPropertyAttributes( aPropertyName );
    }

    void setStepperProperty( String const& aStepperID,
                             String const& aPropertyName,
                             Polymorph const& aValue )
    {
        getStepper( aStepperID )->setProperty( aPropertyName, aValue );
    }

    Polymorph
    getStepperProperty( String const& aStepperID,
                        String const& aPropertyName ) const
    {
        return getStepper( aStepperID )->getProperty( aPropertyName );
    }

    void loadStepperProperty( String const& aStepperID,
                              String const& aPropertyName,
                              Polymorph const& aValue )
    {
        getStepper( aStepperID )->loadProperty( aPropertyName, aValue );
    }

    Polymorph
    saveStepperProperty( String const& aStepperID,
                         String const& aPropertyName ) const
    {
        return getStepper( aStepperID )->saveProperty( aPropertyName );
    }

    String
    getStepperClassName( String const& aStepperID ) const
    {
        return getStepper( aStepperID )->getPropertyInterface().getClassName();
    }

    py::dict getClassInfo( String const& aClassname ) const
    {
        py::dict retval;
        for ( DynamicModuleInfo::EntryIterator* anInfo(
              getPropertyInterface( aClassname ).getInfoFields() );
              anInfo->next(); )
        {
            retval[ PyUnicode_DecodeLatin1( anInfo->current().first.data(),
                                            anInfo->current().first.length(),
                                            NULL ) ] =
                *reinterpret_cast< const libecs::Polymorph* >(
                    anInfo->current().second );
        }
        return retval;
    }

    Polymorph
    getEntityList( String const& anEntityTypeString,
                   String const& aSystemPathString ) const
    {
        const EntityType anEntityType( anEntityTypeString );
        const SystemPath aSystemPath( aSystemPathString );

        if( aSystemPath.size() == 0 )
        {
            PolymorphVector aVector;
            if( anEntityType == EntityType::SYSTEM )
            {
                aVector.push_back( Polymorph( "/" ) );
            }
            return Polymorph( aVector );
        }

        System const* aSystemPtr( getSystem( aSystemPath ) );

        switch( anEntityType )
        {
        case EntityType::VARIABLE:
            return aSystemPtr->getVariableList();
        case EntityType::PROCESS:
            return aSystemPtr->getProcessList();
        case EntityType::SYSTEM:
            return aSystemPtr->getSystemList();
        default:
            break;
        }

        NEVER_GET_HERE;
    }

    std::vector< String >
    getEntityPropertyList( String const& aFullIDString ) const
    {
        return getEntity( FullID( aFullIDString ) )->getPropertyList();
    }

    bool entityExists( String const& aFullIDString ) const
    {
        try
        {
            (void)getEntity( FullID( aFullIDString ) );
        }
        catch( const NotFound& )
        {
            return false;
        }

        return true;
    }

    void setEntityProperty( String const& aFullPNString,
                            Polymorph const& aValue )
    {
        FullPN aFullPN( aFullPNString );
        Entity* const anEntityPtr( getEntity( aFullPN.getFullID() ) );

        anEntityPtr->setProperty( aFullPN.getPropertyName(), aValue );
    }

    Polymorph
    getEntityProperty( String const& aFullPNString ) const
    {
        FullPN aFullPN( aFullPNString );
        Entity const * const anEntityPtr( getEntity( aFullPN.getFullID() ) );

        return anEntityPtr->getProperty( aFullPN.getPropertyName() );
    }

    void loadEntityProperty( String const& aFullPNString,
                             Polymorph const& aValue )
    {
        FullPN aFullPN( aFullPNString );
        Entity* const anEntityPtr( getEntity( aFullPN.getFullID() ) );

        anEntityPtr->loadProperty( aFullPN.getPropertyName(), aValue );
    }

    Polymorph
    saveEntityProperty( String const& aFullPNString ) const
    {
        FullPN aFullPN( aFullPNString );
        Entity const* const anEntityPtr( getEntity( aFullPN.getFullID() ) );

        return anEntityPtr->saveProperty( aFullPN.getPropertyName() );
    }

    PropertyAttributes
    getEntityPropertyAttributes( String const& aFullPNString ) const
    {
        FullPN aFullPN( aFullPNString );
        Entity const* const anEntityPtr( getEntity( aFullPN.getFullID() ) );

        return anEntityPtr->getPropertyAttributes( aFullPN.getPropertyName() );
    }

    String
    getEntityClassName( String const& aFullIDString ) const
    {
        FullID aFullID( aFullIDString );
        Entity const* const anEntityPtr( getEntity( aFullID ) );

        return anEntityPtr->getPropertyInterface().getClassName();
    }

    Logger* createLogger( String const& aFullPNString )
    {
        return createLogger( aFullPNString, Logger::Policy() );
    }

    Logger* createLogger( String const& aFullPNString,
                          Logger::Policy const& aParamList = Logger::Policy() )
    {
        Logger* retval( getLoggerBroker().createLogger(
            FullPN( aFullPNString ), aParamList ) );

        return retval;
    }

    Logger* createLogger( String const& aFullPNString,
                          py::list aParamList )
    {
        if ( !PySequence_Check( aParamList.ptr() )
             || PySequence_Size( aParamList.ptr() ) != 4 )
        {
            THROW_EXCEPTION( Exception,
                             "second argument must be a tuple of 4 items");
        }

        return createLogger( aFullPNString,
                Logger::Policy(
                    PyLong_AsLong( static_cast< py::object >( aParamList[ 0 ] ).ptr() ),
                    PyFloat_AsDouble( static_cast< py::object >( aParamList[ 1 ] ).ptr() ),
                    PyLong_AsLong( static_cast< py::object >( aParamList[ 2 ] ).ptr() ),
                    PyLong_AsLong( static_cast< py::object >( aParamList[ 3 ] ).ptr() ) ) );
    }

    py::list getLoggerList() const
    {
        py::list retval;

        LoggerBroker const& aLoggerBroker( getLoggerBroker() );

        for( LoggerBroker::const_iterator
                i( aLoggerBroker.begin() ), end( aLoggerBroker.end() );
             i != end; ++i )
        {
            retval.append(
                PyUnicode_DecodeLatin1( (*i).first.asString().data(), (*i).first.asString().length(), NULL ) );
        }

        return retval;
    }

    boost::shared_ptr< DataPointVector >
    getLoggerData( String const& aFullPNString ) const
    {
        return getLogger( aFullPNString )->getData();
    }

    boost::shared_ptr< DataPointVector >
    getLoggerData( String const& aFullPNString,
                   Real const& startTime, Real const& endTime ) const
    {
        return getLogger( aFullPNString )->getData( startTime, endTime );
    }

    boost::shared_ptr< DataPointVector >
    getLoggerData( String const& aFullPNString,
                   Real const& start, Real const& end,
                   Real const& interval ) const
    {
        return getLogger( aFullPNString )->getData( start, end, interval );
    }

    Real
    getLoggerStartTime( String const& aFullPNString ) const
    {
        return getLogger( aFullPNString )->getStartTime();
    }

    Real
    getLoggerEndTime( String const& aFullPNString ) const
    {
        return getLogger( aFullPNString )->getEndTime();
    }


    void setLoggerPolicy( String const& aFullPNString,
                          Logger::Policy const& pol )
    {
        // typedef PolymorphValue::Tuple Tuple;
        getLogger( aFullPNString )->setLoggerPolicy( pol );
    }

    void setLoggerPolicy( String const& aFullPNString,
                          py::list aParamList )
    {
        if ( !PySequence_Check( aParamList.ptr() )
            || PySequence_Size( aParamList.ptr() ) != 4 )
        {
            THROW_EXCEPTION( Exception,
                             "second parameter must be a tuple of 4 items");
        }

        return setLoggerPolicy( aFullPNString,
                Logger::Policy(
                    PyLong_AsLong( static_cast< py::object >( aParamList[ 0 ] ).ptr() ),
                    PyFloat_AsDouble( static_cast< py::object >( aParamList[ 1 ] ).ptr() ),
                    PyLong_AsLong( static_cast< py::object >( aParamList[ 2 ] ).ptr() ),
                    PyLong_AsLong( static_cast< py::object >( aParamList[ 3 ] ).ptr() ) ) );
    }

    Logger::Policy
    getLoggerPolicy( String const& aFullPNString ) const
    {
        return getLogger( aFullPNString )->getLoggerPolicy();
    }

    Logger::size_type
    getLoggerSize( String const& aFullPNString ) const
    {
        return getLogger( aFullPNString )->getSize();
    }

    std::pair< Real, String > getNextEvent() const
    {
        StepperEvent const& aNextEvent( getTopEvent() );

        return std::make_pair(
            static_cast< Real >( aNextEvent.getTime() ),
            aNextEvent.getStepper()->getID() );
    }

    py::object getDMInfo() const
    {
        typedef ModuleMaker< EcsObject >::ModuleMap ModuleMap;
        const ModuleMap& modules( theEcsObjectMaker.getModuleMap() );
        py::list retval;

        for( ModuleMap::const_iterator i( modules.begin() );
                    i != modules.end(); ++i )
        {
            const PropertyInterfaceBase* info(
                reinterpret_cast< const PropertyInterfaceBase *>(
                    i->second->getInfo() ) );
            const char* aFilename( i->second->getFileName() );

            retval.append( py::make_tuple(
                py::cast( info->getTypeName() ),
                py::cast( i->second->getModuleName() ),
                py::cast( aFilename ? aFilename: "" ) ) );
        }
        return retval;
        /*
        ecell/_ecs2.cpp:462:16: warning: local variable 'retval' will be copied despite being returned by name [-Wreturn-std-move]
        return retval;
               ^~~~~~
        ecell/_ecs2.cpp:462:16: note: call 'std::move' explicitly to avoid copying
        return retval;
               ^~~~~~
               std::move(retval)
         */
    }

    PropertyInterfaceBase::PropertySlotMap const&
    getPropertyInfo( String const& aClassname ) const
    {
        return getPropertyInterface( aClassname ).getPropertySlotMap();
    }

    Logger* getLogger( String const& aFullPNString ) const
    {
        return getLoggerBroker().getLogger( aFullPNString );
    }

    void removeLogger( String const& aFullPNString )
    {
        getLoggerBroker().removeLogger( FullPN( aFullPNString ) );
    }

    static char getDMSearchPathSeparator()
    {
        return Model::PATH_SEPARATOR;
    }

    AbstractSimulator( ModuleMaker< EcsObject >& maker )
        : Model( maker ) {}

private:
    AbstractSimulator( AbstractSimulator const& );
};










static std::vector<int> getLibECSVersionInfo()
{
    std::vector<int> info{ getMajorVersion(),
                           getMinorVersion(),
                           getMicroVersion()};
    return info;
}





PYBIND11_MODULE(_ecs2, m) {
    m.doc() = "ecs";

    py::class_< PropertyAttributes >( m, "PropertyAttributes")
        .def( py::init< enum PropertySlotBase::Type, bool, bool, bool, bool, bool >())
        .def( "type", &PropertyAttributes::getType )
        .def( "setable", &PropertyAttributes::isSetable )
        .def( "getable", &PropertyAttributes::isGetable )
        .def( "loadable", &PropertyAttributes::isLoadable )
        .def( "savable", &PropertyAttributes::isSavable )
        .def( "dynamic", &PropertyAttributes::isDynamic )
        .def( "__str__", []( PropertyAttributes &self ){
            std::string retval;
            retval += "{type=";
            retval += typeCodeToString( self.getType() );
            retval += ", ";
            retval += "settable="
                      + stringCast( self.isSetable() )
                      + ", ";
            retval += "gettable="
                      + stringCast( self.isGetable() )
                      + ", ";
            retval += "loadable="
                      + stringCast( self.isLoadable() )
                      + ", ";
            retval += "savable="
                      + stringCast( self.isSavable() )
                      + ", ";
            retval += "dynamic="
                      + stringCast( self.isDynamic() )
                      + "}";
            return retval;
        })
        .def("__getitem__", []( PropertyAttributes &self , int idx) {
            switch ( idx )
            {
            case 0:
                return (int)self.isSetable();
            case 1:
                return (int)self.isGetable();
            case 2:
                return (int)self.isLoadable();
            case 3:
                return (int)self.isSavable();
            case 4:
                return (int)self.isDynamic();
            case 5:
                return (int)self.getType();
            }
            throw std::range_error("Index out of bounds");
        })
        /*
        .def( "__iter__", []( PropertyAttributes &self ){
            return PropertyAttributesIterator::create( *PropertyAttributes );
        }) */
        ;

    py::enum_< PropertySlotBase::Type >(m, "PropertyType")
        .value( "POLYMORPH", PropertySlotBase::POLYMORPH )
        .value( "REAL", PropertySlotBase::REAL )
        .value( "INTEGER", PropertySlotBase::INTEGER )
        .value( "STRING", PropertySlotBase::STRING )
        .export_values();

    py::class_< Logger::Policy >( m, "LoggerPolicy")
        .def( py::init<>())
        .def_property( "minimumStep", &Logger::Policy::getMinimumStep,
                                      &Logger::Policy::setMinimumStep )
        .def_property( "minimumTimeInterval",
                       &Logger::Policy::getMinimumTimeInterval,
                       &Logger::Policy::setMinimumTimeInterval )
        .def_property( "continueOnError",
                       &Logger::Policy::doesContinueOnError,
                       &Logger::Policy::setContinueOnError )
        .def_property( "maxSpace",
                       &Logger::Policy::getMaxSpace,
                       &Logger::Policy::setMaxSpace )
        .def( "__getitem__", []( Logger::Policy &self , int idx) {
            switch ( idx )
            {
            case 0:
                return py::cast( self.getMinimumStep());
            case 1:
                return py::cast( self.getMinimumTimeInterval());
            case 2:
                return py::cast( self.doesContinueOnError());
            case 3:
                return py::cast( self.getMaxSpace());
            }

            throw std::range_error("Index out of bounds");
        });

    py::class_< VariableReferences >( m, "VariableReferences" )
        .def( "positiveReferences", []( VariableReferences &self ) {
            Process::VariableReferenceVector const& refs(
                    self.theProc->getVariableReferenceVector() );
            py::list retval;
            std::for_each(
                refs.begin() + self.theProc->getPositiveVariableReferenceOffset(),
                refs.end(),
                [ &retval ]( VariableReference r ){
                    retval.append( r );
            });
            return retval;
        })

        .def( "zeroReferences", []( VariableReferences &self ) {
            Process::VariableReferenceVector const& refs(
                   self.theProc->getVariableReferenceVector() );
            py::list retval;
            std::for_each(
                refs.begin() + self.theProc->getZeroVariableReferenceOffset(),
                refs.begin() + self.theProc->getPositiveVariableReferenceOffset(),
                [ &retval ]( VariableReference r ){
                    retval.append( r );
            });
            return retval;
        })
        .def( "negativeReferences", []( VariableReferences &self ) {
            Process::VariableReferenceVector const& refs(
                    self.theProc->getVariableReferenceVector() );
            py::list retval;
            std::for_each(
                refs.begin(),
                refs.begin() + self.theProc->getZeroVariableReferenceOffset(),
                [ &retval ]( VariableReference r ){
                    retval.append( r ); }
            );
            return retval;
        })
        .def( "add", []( VariableReferences &self, String const& name, String const& fullID, Integer const& coef, bool isAccessor ) {
                  return (Integer)(self.theProc->registerVariableReference( name, FullID( fullID ), coef, isAccessor ));
        })
        .def( "add", []( VariableReferences &self, String const& name, String const& fullID, Integer const& coef ) {
                  return (Integer)(self.theProc->registerVariableReference( name, FullID( fullID ), coef, false ));
        })
        .def( "add", []( VariableReferences &self, String const& fullID, Integer const& coef, bool isAccessor ) {
                  return (Integer)(self.theProc->registerVariableReference( FullID( fullID ), coef, isAccessor ));
        })
        .def( "add", []( VariableReferences &self, String const& fullID, Integer const& coef ) {
                  return (Integer)(self.theProc->registerVariableReference( FullID( fullID ), coef, false ));
        })
        .def( "add", []( VariableReferences &self, String const& name, Variable* var, Integer const& coef, bool isAccessor ) {
                  return (Integer)(self.theProc->registerVariableReference( name, var, coef, isAccessor ));
        } )
        .def( "add", []( VariableReferences &self, String const& name, Variable* var, Integer const& coef ) {
                  return (Integer)(self.theProc->registerVariableReference( name, var, coef, false ));
        } )
        .def( "add", []( VariableReferences &self, Variable* var, Integer const& coef, bool isAccessor ) {
                  return (Integer)(self.theProc->registerVariableReference( var, coef, isAccessor ));
        } )
        .def( "add", []( VariableReferences &self, Variable* var, Integer const& coef ) {
                  return (Integer)(self.theProc->registerVariableReference( var, coef, false ));
        } )
        .def( "remove", []( VariableReferences &self, String const& name ) {
                  self.theProc->removeVariableReference( name );
        } )
        .def( "remove", []( VariableReferences &self, Integer const id ) {
                  self.theProc->removeVariableReference( id );
        } )
        .def( "__getitem__", []( VariableReferences &self, py::object name ) {
            if ( PyLong_Check( name.ptr() ) )
            {
                Integer id( PyLong_AS_LONG( name.ptr() ) );
                return self.theProc->getVariableReference( id );
            }
            else if ( PyBytes_Check( name.ptr() ) )
            {
                std::string nameStr( PyBytes_AS_STRING( name.ptr() ),
                                     PyBytes_GET_SIZE( name.ptr() ) );
                return self.theProc->getVariableReference( nameStr );
            }
            PyErr_SetString( PyExc_TypeError,
                             "The argument is neither an integer nor a string" );
            throw py::error_already_set();
            // throw std::exception();
        },
              py::return_value_policy::automatic_reference )
        .def( "__len__", []( VariableReferences &self ) {
            return self.theProc->getVariableReferenceVector().size();
        } )
        /*
        .def( "__iter__", []( VariableReferences &self ) {
            return STLIteratorWrapper< Process::VariableReferenceVector::const_iterator >::create( self.theProc->getVariableReferenceVector() );
        } )*/
        .def( "__str__", []( VariableReferences &self ) {
            Process::VariableReferenceVector const& refs(
                    self.theProc->getVariableReferenceVector() );
            std::string retval;
            retval += '[';
            for ( Process::VariableReferenceVector::const_iterator
                    b( refs.begin() ), i( b ), e( refs.end() );
                    i != e; ++i )
            {
                if ( i != b )
                    retval += ", ";
                retval += VariableReference___str__( &*i );
            }
            retval += ']';

            return retval;
        } )
        ;

    py::class_< VariableReference >( m, "VariableReference")
        .def( "coefficient", &VariableReference::getCoefficient )
        .def( "serial",      &VariableReference::getSerial )
        .def( "name",        &VariableReference::getName )
        .def( "isAccessor",  &VariableReference::isAccessor )
        /* TODO py::make_function */
        .def( "FullID",      &VariableReference::getFullID,
                             py::return_value_policy::automatic_reference )
        /* TODO py::make_function */
        .def( "variable",    &VariableReference::getVariable,
                             py::return_value_policy::take_ownership )
        .def( "__str__",     &VariableReference___str__ )
        ;

// return_copy_const_reference  ->  py::return_value_policy< py::copy_const_reference >
// return_existing_object -> py::return_value_policy< py::reference_existing_object >

    py::class_< Stepper >( m, "Stepper")
    //py::class_< Stepper, py::bases<>, Stepper, boost::noncopyable >( "Stepper", py::no_init )
        .def_property( "id", &Stepper::getID, &Stepper::setID )
        .def_property( "Priority",
                       &Stepper::getPriority,
                       &Stepper::setPriority )
        .def_property( "StepInterval",
                       &Stepper::getStepInterval,
                       &Stepper::setStepInterval )
        .def_property( "MaxStepInterval",
                       &Stepper::getMaxStepInterval,
                       &Stepper::setMaxStepInterval )
        .def_property( "MinStepInterval",
                       &Stepper::getMinStepInterval,
                       &Stepper::setMinStepInterval )
        .def_property( "RngSeed",
                       [](){
                         PyErr_SetString( PyExc_AttributeError, "Write-only attributes." );
                         return py::handle( Py_None ).inc_ref();
                       },
                       &Stepper::setRngSeed )
        .def( "__setattr__", []( Stepper &self, py::object key, py::object value ) {
            self.setProperty( key.cast< std::string >(), value.cast< Polymorph >() );
            /*
            以下に記載された不具合の解消と思われる。一旦コメントアウト
            https://moriyoshi.hatenablog.com/entry/20091119/1258609766
            try
            {

                // 引数 key から self の属性値のポインタを取得
                py::handle aDescr( PyObject_GetAttr(
                    reinterpret_cast< PyObject* >( Py_TYPE( self ) ),
                    key.ptr()
                ) );
                //if ( !aDescr || !( aDescr->ob_type->tp_flags & Py_TPFLAGS_HAVE_CLASS ) || !aDescr.get()->ob_type->tp_descr_set )
                // A simple "->ob_type" remains here.
                if ( !aDescr ||
                     !( aDescr.ptr()->ob_type->tp_flags & Py_TPFLAGS_HAVE_CLASS ) ||
                     !aDescr.ptr()->ob_type->tp_descr_set )
                {
                    PyErr_Clear();
                    std::string keyStr = key.cast< std::string >();
                    self->setProperty( keyStr, value.cast< Polymorph >() );
                }
                else
                {
                    Py_TYPE( aDescr.ptr() )->tp_descr_set( aDescr.ptr() ), self, value.ptr() );
                    if (PyErr_Occurred())
                    {
                        throw py::error_already_set();
                    }
                }
            }
            catch ( NoSlot const& anException )
            {
                PyErr_SetString( PyExc_AttributeError, anException.what() );
                throw py::error_already_set();
            }
            */
        })
        .def( "__getattr__", []( Stepper &self, std::string key ) {
            try {
                if ( key == "__members__" || key == "__methods__" )
                {
                    PyErr_SetString( PyExc_KeyError, key.c_str() );
                    throw py::error_already_set();
                }

                return self.getProperty( key );
            }
            catch ( NoSlot const& anException ) {
                PyErr_SetString( PyExc_AttributeError, anException.what() );
                throw py::error_already_set();
                return Polymorph();
            }
        });

    py::class_< Entity >( m, "Entity")
    //py::class_< Entity, py::bases<>, Entity, boost::noncopyable >( "Entity", py::no_init )
        // properties
        .def( "model", []( Entity const& self ){
            return dynamic_cast<AbstractSimulator*>(self.getModel());
        }, py::return_value_policy::take_ownership )
        // TODO BUG?? Entity_getModel -> getSimulator
        .def( "simulator", []( Entity const& self ){
            return dynamic_cast<AbstractSimulator*>(self.getModel());
        }, py::return_value_policy::take_ownership )
        .def( "superSystem", &Entity::getSuperSystem,
                     py::return_value_policy::take_ownership )
        .def_property( "ID", &Entity::getID, &Entity::setID )
        .def( "FullID", &Entity::getFullID )
        .def_property( "Name", &Entity::getName, &Entity::setName )
        .def( "getSuperSystem", &Entity::getSuperSystem,
                     py::return_value_policy::take_ownership )
        .def( "__setattr__", []( Entity &self, py::object key, py::object value ) {
            self.setProperty( key.cast< std::string >(), value.cast< Polymorph >() );
        })
        .def( "__getattr__", []( Entity &self, std::string key ) {
            try {
                if ( key == "__members__" || key == "__methods__" )
                {
                    PyErr_SetString( PyExc_KeyError, key.c_str() );
                    throw py::error_already_set();
                }
                return self.getProperty( key );
            }
            catch ( NoSlot const& anException ) {
                PyErr_SetString( PyExc_AttributeError, anException.what() );
                throw py::error_already_set();
                return Polymorph();
            }
        })
        ;

    py::class_< System, Entity >( m, "Entity")
    // py::class_< System, py::bases< Entity >, System, boost::noncopyable>( "System", py::no_init )
        .def( "Size", &System::getSize )
        .def( "SizeN_A", &System::getSizeN_A )
        .def_property( "StepperID", &System::getStepperID, &System::setStepperID )
        .def( "registerEntity", ( void( System::* )( Entity* ) )&System::registerEntity )
        .def( "configureSize", &System::configureSizeVariable )
        ;

    py::class_< Process, Entity >( m, "Process")
    // py::class_< Process, py::bases< Entity >, Process, boost::noncopyable >( "Process", py::no_init )
        .def_property( "Activity",  &Process::getActivity,
                                    &Process::setActivity )
        .def( "IsContinuous", &Process::isContinuous )
        .def_property( "Priority",  &Process::getPriority,
                                    &Process::setPriority )
        .def_property( "StepperID", &Process::getStepperID,
                                    &Process::setStepperID )
        .def( "variableReferences", []( Process *self ){
            return py::cast( VariableReferences( self ) );
        } ) ;

    py::class_< Variable, Entity >( m, "Variable")
    //py::class_< Variable, py::bases< Entity >, Variable, boost::noncopyable >( "Variable", py::no_init )
        .def_property( "Value",  &Variable::getValue,
                                 &Variable::setValue )
        .def_property( "MolarConc",  &Variable::getMolarConc,
                                     &Variable::setMolarConc  )
        .def_property( "NumberConc", &Variable::getNumberConc,
                                     &Variable::setNumberConc )
        ;








    m.def("getLibECSVersionInfo", &getLibECSVersionInfo,
            "A function which return libecs version information");
    m.def("getLibECSVersion", &getVersion );
    m.def("setWarningHandler", &setWarningHandler );

}
