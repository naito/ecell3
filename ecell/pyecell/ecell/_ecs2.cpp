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
            py::error_already_set();
            throw std::exception();
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





    m.def("getLibECSVersionInfo", &getLibECSVersionInfo,
            "A function which return libecs version information");
    m.def("getLibECSVersion", &getVersion );
    m.def("setWarningHandler", &setWarningHandler );

}
