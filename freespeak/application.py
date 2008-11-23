# FreeSpeak - a GUI frontend to online translator engines
# freespeak/application.py
#
## Copyright (C) 2005-2008  Luca Bruno <lethalman88@gmail.com>
##
## This file is part of FreeSpeak.
##   
## FreeSpeak is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##    
## FreeSpeak is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Library General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

from freespeak import defs

__author__ = "Luca Bruno <lethalman88@gmail.com>"
__version__ = defs.VERSION
__homepage__ = "http://home.gna.org/freespeak"

import gettext
import tempfile
import sys
import os
from optparse import OptionParser
import time

import gobject
import gtk
from gtk import gdk
import dbus
import dbus.service
import dbus.mainloop.glib

from freespeak import defs
from freespeak.config import Config
from freespeak.translator import TranslatorsManager
import freespeak.translators
from freespeak.ui.main_window import MainWindow
from freespeak.ui import exception_dialog
from freespeak.ui import style

class ClipboardController (object):
    # Get from PRIMARY, save to both PRIMARY and CLIPBOARD
    def __init__ (self, application):
        self.application = application
        self.clipboard = gtk.clipboard_get ('CLIPBOARD')
        self.primary = gtk.clipboard_get ('PRIMARY')
        self.cur_contents = None

    def get_contents (self, force=False):
        if force or (self.application.config.get ('get_clipboard') and self.primary.wait_is_text_available ()):
            text = self.primary.wait_for_text ()
            if force or (text != self.cur_contents):
                self.cur_contents = text
                return text

    def set_contents (self, contents, force=False):
        if force or self.application.config.get ('set_clipboard'):
            self.cur_contents = contents
            self.primary.set_text (contents)
            self.clipboard.set_text (contents)

class Application (dbus.service.Object):
    version = __version__

    def __init__ (self, bus, path, name, options={}, args=[]):
        dbus.service.Object.__init__ (self, bus, path, name)
        self.domain = defs.GETTEXT_PACKAGE
        self.options = options
        self.args = args

        self.setup_l10n ()
        self.setup_exception_dialog ()
        self.setup_config ()
        self.setup_paths ()
        self.setup_icons ()
        self.setup_translators_manager ()
        self.setup_clipboard ()
        self.setup_style ()

        self.running = False

    def setup_exception_dialog (self):
        sys.excepthook = exception_dialog.exception_hook

    @staticmethod
    def setup_l10n ():
        gettext.install (defs.GETTEXT_PACKAGE, unicode=True)

    def setup_config (self):
        self.config = Config ()

    def setup_paths (self):
        self.icons_path = os.path.join (defs.DATA_DIR, defs.PACKAGE, 'art')
        self.translators_path = os.path.dirname (freespeak.translators.__file__)

    def setup_icons (self):
        self.icon_theme = gtk.icon_theme_get_default ()
        self.icon_theme.append_search_path (self.icons_path)
        gtk.window_set_default_icon (self.icon_theme.load_icon (defs.PACKAGE, 64, 0))

    def setup_translators_manager (self):
        self.translators_manager = TranslatorsManager (self)

    def setup_clipboard (self):
        self.clipboard = ClipboardController (self)

    def setup_style (self):
        style.setup_rc ()

    @dbus.service.method ("org.gna.FreeSpeak",
                          in_signature='', out_signature='b')
    def is_running (self):
        return self.running

    @dbus.service.method ("org.gna.FreeSpeak",
                          in_signature='a{sv}asi', out_signature='')
    def start (self, options={}, args=[], timestamp=None):
        if self.running:
            if not timestamp:
                timestamp = int (time.time ())
            self.main_window.present_with_time (timestamp)
            return

        gtk.gdk.threads_init()

        self.main_window = MainWindow (self)
        self.main_window.show ()

        self.running = True

        gtk.main ()

        self.running = False

    @dbus.service.method ("org.gna.FreeSpeak",
                          in_signature='', out_signature='')
    def stop (self):
        if self.running:
            gtk.main_quit ()

def get_instance ():
    """
    Get the DBUS instance of the application.
    org.gna.FreeSpeak at path / with interface org.gna.FreeSpeak
    """
    dbus.mainloop.glib.DBusGMainLoop (set_as_default=True)
    bus = dbus.SessionBus ()
    request = bus.request_name ("org.gna.FreeSpeak", dbus.bus.NAME_FLAG_DO_NOT_QUEUE)
    if request != dbus.bus.REQUEST_NAME_REPLY_EXISTS:
        application = Application (bus, '/', "org.gna.FreeSpeak")
    else:
        object = bus.get_object ("org.gna.FreeSpeak", "/")
        application = dbus.Interface (object, "org.gna.FreeSpeak")
    return application

__all__ = ['get_instance']
