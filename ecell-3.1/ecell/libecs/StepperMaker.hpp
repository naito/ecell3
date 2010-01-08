//::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
//
//       This file is part of the E-Cell System
//
//       Copyright (C) 1996-2010 Keio University
//       Copyright (C) 2005-2009 The Molecular Sciences Institute
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

#ifndef ___STEPPERMAKER_H___
#define ___STEPPERMAKER_H___

#include "Stepper.hpp"
#include "PropertiedObjectMaker.hpp"

namespace libecs
{

  /* *defgroup libecs_module The Libecs Module 
   * This is the libecs module 
   * @{ 
   */ 
  

  class LIBECS_API StepperMaker 
  {
  private:
    PropertiedObjectMaker& theBackend;

  protected:
    virtual void makeClassList();

  public:
    StepperMaker( PropertiedObjectMaker& maker );
    virtual ~StepperMaker();
    Stepper* make( const std::string& aClassName );
    const PropertiedObjectMaker::SharedModule& getModule(
	const std::string& aClassName, bool forceReload );
  };

  /** @} */ //end of libecs_module 
  
} // namespace libecs


#endif /* ___STEPPERMAKER_H___ */