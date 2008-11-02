SUBDIRS = art

# *****************************************************************************
# GConf Schemas
# *****************************************************************************
# GConf Preference Schemas
schemadir = $(GCONF_SCHEMA_FILE_DIR)
schema_in_files = freespeak.schemas.in
schema_DATA = $(schema_in_files:.schemas.in=.schemas)

# *****************************************************************************
# Build rules
# *****************************************************************************
@INTLTOOL_SCHEMAS_RULE@

if GCONF_SCHEMAS_INSTALL
install-data-local: install-schemas
install-schemas:
	GCONF_CONFIG_SOURCE=$(GCONF_SCHEMA_CONFIG_SOURCE) \
                $(GCONFTOOL) --makefile-install-rule $(schema_DATA)
endif

DISTCLEANFILES =	\
	$(schema_DATA)

EXTRA_DIST =	\
	$(schema_in_files)