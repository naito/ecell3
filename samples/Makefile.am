samplesdir = $(docdir)/samples

SAMPLES = \
	CoupledOscillator \
	Drosophila \
	Drosophila-cpp \
	Gauss-Newton \
	Heinrich \
	LTD \
	Pendulum \
	SRES \
	SSystem \
	Toy_Hybrid \
	branchG \
	ga \
	ga-deap \
	heatshock \
	session_manager \
	simple \
	steady_state \
	tauleap

EXTRA_DIST = $(SAMPLES)

install-data-hook:
	[ ! -e "$(DESTDIR)$(samplesdir)" ] && $(top_srcdir)/install-sh -d "$(DESTDIR)$(samplesdir)"; \
	for dir in $(SAMPLES); do \
		[ ! -e "$(DESTDIR)$(samplesdir)/$$dir" ] && \
			$(top_srcdir)/install-sh -d "$(DESTDIR)$(samplesdir)/$$dir"; \
		for file in "$$dir"/*; do \
			if [ -f "$$file" ]; then \
				$(INSTALL_DATA) "$$file" "$(DESTDIR)$(samplesdir)/$$dir"; \
			elif [ -d "$$file" ]; then \
				[ ! -e "$(DESTDIR)$(samplesdir)/$$file" ] && \
					$(top_srcdir)/install-sh -d "$(DESTDIR)$(samplesdir)/$$file"; \
				for file in "$$file"/*; do \
					$(INSTALL_DATA) "$$file" "$(DESTDIR)$(samplesdir)/$$file"; \
				done; \
			fi; \
		done; \
	done

uninstall-hook:
	$(RM) -r $(DESTDIR)$(samplesdir)

dist-hook:
	for dir in $(SAMPLES); do \
		find "$(distdir)/$$dir" -name ".svn" -type d | while read file; do \
			rm -rf "$$file"; \
		done; \
	done
