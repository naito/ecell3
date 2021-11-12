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

static std::vector<std::string> getLibECSVersionInfo()
{
    std::vector<std::string> info{ libecs::getMajorVersion(),
                                   libecs::getMinorVersion(),
                                   libecs::getMicroVersion()};
    return info;
}

PYBIND11_MODULE(_ecs2, m) {
  m.doc() = "ecs";
  m.def("getLibECSVersionInfo", &getLibECSVersionInfo,
    "A function which return libecs version information");
}
