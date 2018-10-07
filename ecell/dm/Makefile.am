abs_top_builddir = @abs_top_builddir@

SUFFIXES = .cpp $(LTDL_SHLIB_EXT)

SHELL = @SHELL@

AM_CXXFLAGS = @CXXFLAGS@

ECELL3_DMC = $(top_builddir)/pyecell/ecell3-python ../bin/ecell3-dmc

ECELL_DIRNAME = @ECELL_DIRNAME@

DM_SO_DIR = ${libdir}/${ECELL_DIRNAME}/dms
DM_SRC_DIR =  ${datadir}/${ECELL_DIRNAME}/dms

PYTHON_INCLUDES = @PYTHON_INCLUDES@
PYTHON_LIBS = @PYTHON_LIBS@

LTDL_SHLIB_MD_EXT = .o.d

DMS = \
	ConstantFluxProcess.cpp \
	DAEStepper.cpp \
	DecayFluxProcess.cpp \
	ESSYNSStepper.cpp \
	ExpressionAlgebraicProcess.cpp \
	ExpressionAssignmentProcess.cpp \
	ExpressionEventProcess.cpp \
	ExpressionFluxProcess.cpp \
	FixedDAE1Stepper.cpp \
	FixedODE1Stepper.cpp \
	FluxDistributionStepper.cpp \
	GMAProcess.cpp \
	GillespieProcess.cpp \
	MassActionFluxProcess.cpp \
	MichaelisUniUniFluxProcess.cpp \
	ODE23Stepper.cpp \
	ODE45Stepper.cpp \
	ODEStepper.cpp \
	PingPongBiBiFluxProcess.cpp \
	QuasiDynamicFluxProcess.cpp \
	SSystemProcess.cpp \
	TauLeapProcess.cpp \
	TauLeapStepper.cpp

DMH = \
	ESSYNSProcessInterface.hpp \
	ExpressionProcessBase.hpp \
	SingleExpressionProcessBase.hpp \
	GillespieProcess.hpp \
	GillespieProcessInterface.hpp \
	QuasiDynamicFluxProcess.hpp \
	QuasiDynamicFluxProcessInterface.hpp

SOS = \
	MassActionFluxProcess$(LTDL_SHLIB_EXT) \
	MichaelisUniUniFluxProcess$(LTDL_SHLIB_EXT) \
	ConstantFluxProcess$(LTDL_SHLIB_EXT) \
	DecayFluxProcess$(LTDL_SHLIB_EXT) \
	SSystemProcess$(LTDL_SHLIB_EXT) \
	GillespieProcess$(LTDL_SHLIB_EXT) \
	TauLeapProcess$(LTDL_SHLIB_EXT) \
	TauLeapStepper$(LTDL_SHLIB_EXT) \
	FixedODE1Stepper$(LTDL_SHLIB_EXT) \
	FixedDAE1Stepper$(LTDL_SHLIB_EXT) \
	ODE23Stepper$(LTDL_SHLIB_EXT) \
	ODE45Stepper$(LTDL_SHLIB_EXT) \
	DAEStepper$(LTDL_SHLIB_EXT) \
	ODEStepper$(LTDL_SHLIB_EXT) \
	ESSYNSStepper$(LTDL_SHLIB_EXT) \
	GMAProcess$(LTDL_SHLIB_EXT) \
	SSystemProcess$(LTDL_SHLIB_EXT) \
	FluxDistributionStepper$(LTDL_SHLIB_EXT) \
	QuasiDynamicFluxProcess$(LTDL_SHLIB_EXT) \
	ExpressionFluxProcess$(LTDL_SHLIB_EXT) \
	ExpressionAlgebraicProcess$(LTDL_SHLIB_EXT) \
	ExpressionAssignmentProcess$(LTDL_SHLIB_EXT) \
	ExpressionEventProcess$(LTDL_SHLIB_EXT)

ODS = \
	MassActionFluxProcess$(LTDL_SHLIB_MD_EXT) \
	MichaelisUniUniFluxProcess$(LTDL_SHLIB_MD_EXT) \
	ConstantFluxProcess$(LTDL_SHLIB_MD_EXT) \
	DecayFluxProcess$(LTDL_SHLIB_MD_EXT) \
	SSystemProcess$(LTDL_SHLIB_MD_EXT) \
	GillespieProcess$(LTDL_SHLIB_MD_EXT) \
	TauLeapProcess$(LTDL_SHLIB_MD_EXT) \
	TauLeapStepper$(LTDL_SHLIB_MD_EXT) \
	FixedODE1Stepper$(LTDL_SHLIB_MD_EXT) \
	FixedDAE1Stepper$(LTDL_SHLIB_MD_EXT) \
	ODE23Stepper$(LTDL_SHLIB_MD_EXT) \
	ODE45Stepper$(LTDL_SHLIB_MD_EXT) \
	DAEStepper$(LTDL_SHLIB_MD_EXT) \
	ODEStepper$(LTDL_SHLIB_MD_EXT) \
	ESSYNSStepper$(LTDL_SHLIB_MD_EXT) \
	GMAProcess$(LTDL_SHLIB_MD_EXT) \
	SSystemProcess$(LTDL_SHLIB_MD_EXT) \
	FluxDistributionStepper$(LTDL_SHLIB_MD_EXT) \
	QuasiDynamicFluxProcess$(LTDL_SHLIB_MD_EXT) \
	ExpressionFluxProcess$(LTDL_SHLIB_MD_EXT) \
	ExpressionAlgebraicProcess$(LTDL_SHLIB_MD_EXT) \
	ExpressionAssignmentProcess$(LTDL_SHLIB_MD_EXT) \
	ExpressionEventProcess$(LTDL_SHLIB_MD_EXT)

EXTRA_DIST = ${DMS} ${DMH}
dmdir = ${DM_SRC_DIR}
dm_DATA = ${DMS} ${DMH}

dmsodir = ${DM_SO_DIR}
dmso_DATA = ${DESCS}

all-local: $(SOS)

.cpp$(LTDL_SHLIB_EXT):
	${ECELL3_DMC} --verbose --dmcompile="../../dmtool" --no-stdinclude --no-stdlibdir --ldflags="-L$(abs_top_builddir)/tmp$(libdir) $(LIBS) $(EXTRA_LDFLAGS)" --cxxflags='${CPPFLAGS} ${CXXFLAGS} $(EXTRA_CXXFLAGS) -I${top_srcdir}/libecs -I${top_srcdir}/.. -I${top_srcdir} -I${top_srcdir}/../libltdl  ${PYTHON_INCLUDES} ' -o $@ $<

# This install customization is needed because DLL's cannot be loaded by
# LoadLibrary() without executable flags set to them under Windows NT.
install-data-local:
	test -z "$(dmsodir)" || $(mkdir_p) "$(DESTDIR)$(dmsodir)"
	@for p in $(SOS); do \
		if test -f "$$p"; then d=; else d="$(srcdir)/"; fi; \
		$(am__strip_dir) \
		echo " ${INSTALL} -m 755 '$$d$$p' '$(DESTDIR)$(dmsodir)/$$f'"; \
		${INSTALL} -m 755 "$$d$$p" "$(DESTDIR)$(dmsodir)/$$f"; \
	done

uninstall-local:
	@for p in $(SOS); do \
		$(am__strip_dir) \
		echo " rm -f '$(DESTDIR)$(dmsodir)/$$f'"; \
		$(RM) "$(DESTDIR)$(dmsodir)/$$f"; \
	done

clean-local:
	${RM} -rf ${SOS}
	${RM} -rf ${ODS}
