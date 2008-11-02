16icondir = $(datadir)/icons/hicolor/16x16/apps
16icon_DATA = 16x16/freespeak.png

64icondir = $(datadir)/icons/hicolor/64x64/apps
64icon_DATA = 64x64/freespeak.png

install-data-hook: update-icon-cache
uninstall-hook: update-icon-cache
update-icon-cache:
	@-if test -z "$(DESTDIR)"; then \
		echo "Updating Gtk icon cache."; \
		$(gtk_update_icon_cache); \
	else \
		echo "*** Icon cache not updated.  After (un)install, run this:" \
		echo "***   $(gtk_update_icon_cache)"; \
	fi

EXTRA_DIST = \
	$(16icon_DATA) \
	$(64icon_DATA)