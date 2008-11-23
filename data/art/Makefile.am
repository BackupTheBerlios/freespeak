artdir = $(pkgdatadir)/art
art_DATA = \
	google.png \
	yahoo.png \
	freetranslation.png

16icondir = $(datadir)/icons/hicolor/16x16/apps
16icon_DATA = 16x16/freespeak.png

24icondir = $(datadir)/icons/hicolor/24x24/apps
24icon_DATA = 24x24/freespeak.png

32icondir = $(datadir)/icons/hicolor/32x32/apps
32icon_DATA = 32x32/freespeak.png

48icondir = $(datadir)/icons/hicolor/48x48/apps
48icon_DATA = 48x48/freespeak.png

64icondir = $(datadir)/icons/hicolor/64x64/apps
64icon_DATA = 64x64/freespeak.png

gtk_update_icon_cache = gtk-update-icon-cache -f -t $(datadir)/icons/hicolor

install-data-hook: update-icon-cache
uninstall-hook: update-icon-cache
update-icon-cache:
	@-if test -z "$(DESTDIR)"; then \
		echo "Updating Gtk icon cache."; \
		$(gtk_update_icon_cache); \
	else \
		echo "*** Icon cache not updated.  After (un)install, run this:"; \
		echo "***   $(gtk_update_icon_cache)"; \
	fi

EXTRA_DIST = \
	$(16icon_DATA) \
	$(24icon_DATA) \
	$(32icon_DATA) \
	$(48icon_DATA) \
	$(64icon_DATA) \
	$(art_DATA)