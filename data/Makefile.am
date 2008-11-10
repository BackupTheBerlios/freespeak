SUBDIRS = art

# *****************************************************************************
# Desktop files
# *****************************************************************************
desktopdir = $(datadir)/applications
desktop_in_files = freespeak.desktop.in
desktop_DATA = $(desktop_in_files:.desktop.in=.desktop)
@INTLTOOL_DESKTOP_RULE@

# *****************************************************************************
# GConf Schemas
# *****************************************************************************
schemadir = $(GCONF_SCHEMA_FILE_DIR)
schema_in_files = freespeak.schemas.in
schema_DATA = $(schema_in_files:.schemas.in=.schemas)
@INTLTOOL_SCHEMAS_RULE@

# *****************************************************************************
# Build rules
# *****************************************************************************

if GCONF_SCHEMAS_INSTALL
install-data-local: install-schemas
install-schemas:
	if test -z "$(DESTDIR)" ; then \
		GCONF_CONFIG_SOURCE=$(GCONF_SCHEMA_CONFIG_SOURCE) \
		        $(GCONFTOOL) --makefile-install-rule $(schema_DATA) ; \
	fi
endif

DISTCLEANFILES =	\
	$(schema_DATA) \
	$(desktop_DATA)

EXTRA_DIST =	\
	$(desktop_in_files) \
	$(schema_in_files)