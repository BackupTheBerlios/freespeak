# FreeSpeak - a simple frontend to already existing online translators
# application.py

#     Copyright (C) 2005-2006-2007-2008  Luca Bruno <lethalman88@gmail.com>
   
#     This program is free software; you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation; either version 2 of the License, or
#     (at your option) any later version.
    
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Library General Public License for more details.

#     You should have received a copy of the GNU General Public License
#     along with this program; if not, write to the Free Software
#     Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

from freespeak import defs

__author__ = "Luca Bruno <lethalman88@gmail.com>"
__version__ = defs.VERSION
__homepage__ = "http://home.gna.org/freespeak"

import gettext
import tempfile
import sys
import os
from optparse import OptionParser

import gtk
from gtk import gdk

from freespeak import defs
from freespeak.config import Config
from freespeak.translator import TranslatorsManager
import freespeak.translators
from freespeak.ui.main_window import MainWindow
from freespeak.ui import exception_dialog
from freespeak.ui import style

class ClipboardController (gtk.Clipboard):
    def __init__ (self, application):
        gtk.Clipboard.__init__ (self)
        self.application = application
        self.cur_contents = None

    def get_contents (self):
        if self.application.config.get ('get_clipboard') and self.wait_is_text_available ():
            text = self.wait_for_text ()
            if text != self.cur_contents:
                self.cur_contents = text
                return text

    def set_contents (self, contents):
        if self.application.config.get ('set_clipboard'):
            self.cur_contents = contents
            self.set_text (contents)

class Application (object):
    version = __version__

    def __init__ (self, options={}, args=[]):
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

        self.started = False

    def setup_exception_dialog (self):
        sys.excepthook = exception_dialog.exception_hook

    def setup_l10n (self):
        gettext.install (self.domain, unicode=True)

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

    def start (self):
        gtk.gdk.threads_init()
        self.main_window = MainWindow (self)
        self.main_window.show ()

        self.started = True

        gtk.gdk.threads_enter()
        gtk.main ()
        gtk.gdk.threads_leave()

    def stop (self):
        if self.started:
            gtk.main_quit ()
