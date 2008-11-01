"""
FreeSpeak - a simple frontend to already existing online translators
application.py

    Copyright (C) 2005-2006-2007-2008  Luca Bruno <lethalman88@gmail.com>
   
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Library General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
"""

__author__ = "Luca Bruno <lethalman88@gmail.com>"
__version__ = "0.1.1"
__homepage__ = "http://home.gna.org/freespeak"

import gettext
import tempfile
import sys
import os
from optparse import OptionParser

import gtk
from gtk import gdk

from freespeak.config import Config
from freespeak.translator import TranslatorsManager
import freespeak.translators
from freespeak.ui.main_window import MainWindow
from freespeak.ui import exception_dialog

class Application (object):
    version = __version__

    def __init__ (self, options={}, args=[]):
        self.domain = 'freespeak'
        self.options = options
        self.args = args

        self.setup_l10n ()
        self.setup_exception_dialog ()
        self.setup_config ()
        self.setup_paths ()
        self.setup_icons ()
        self.setup_translators_manager ()

        self.started = False

    def setup_exception_dialog (self):
        sys.excepthook = exception_dialog.exception_hook

    def setup_l10n (self):
        gettext.NullTranslations ()
        gettext.install (self.domain)

    def setup_config (self):
        self.config = Config ()

    def setup_paths (self):
        self.icons_path = os.path.join (sys.prefix, 'share', 'freespeak', 'icons')
        self.translators_path = os.path.dirname (freespeak.translators.__file__)

    def setup_icons (self):
        self.icon_factory = gtk.IconFactory ()
        for stock, src in {'freespeak-icon': "freespeak-16x16.png"}.iteritems ():
            file = os.path.join (self.icons_path, src)
            if os.path.isfile (file):
                self.icon_factory.add (stock,
                                       gtk.IconSet (gdk.pixbuf_from_file (file)))
        self.icon_factory.add_default ()

    def setup_translators_manager (self):
        self.translators_manager = TranslatorsManager (self)

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
