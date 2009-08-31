# FreeSpeak - a GUI frontend to online translator engines
# freespeak/application.py
#
## Copyright (C) 2005, 2006, 2007, 2008, 2009  Luca Bruno <lethalman88@gmail.com>
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
## Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA.

"""
Launch and manage the FreeSpeak Application.
Application is a singleton and it can be a DBus object.
For more information please visit the homepage at http://freespeak.berlios.de
"""

from freespeak import defs

__author__ = "Luca Bruno <lethalman88@gmail.com>"
__version__ = defs.VERSION

import gettext
import sys
import os
import time

import gtk
import dbus
import dbus.service
import dbus.mainloop.glib

from freespeak.config import Config
from freespeak.translator import TranslatorsManager
import freespeak.translators
from freespeak.ui.globalkeybinding import GlobalKeyBinding
from freespeak.ui.main_window import MainWindow
from freespeak.ui import exception_dialog
from freespeak.ui import style

class ClipboardController (object):
    """
    A higher layer on top of GTK+ clipboards for FreeSpeak usage.
    """

    # Get from PRIMARY, save to both PRIMARY and CLIPBOARD
    def __init__ (self, application):
        self.application = application
        self.clipboard = gtk.clipboard_get ('CLIPBOARD')
        self.primary = gtk.clipboard_get ('PRIMARY')
        self.cur_contents = None

    def get_contents (self):
        """
        Get the contents from the primary clipboard if new text is available
        and if the 'get_clipboard' setting is on.
        """
        get_clipboard = self.application.config.get ('get_clipboard')
        clipboard_text_available = self.primary.wait_is_text_available ()
        if get_clipboard and clipboard_text_available:
            text = self.primary.wait_for_text ()
            self.cur_contents = text
            return text

    def has_text_contents (self):
        """
        Check whether the primary clipboard has new valid text available.
        """
        if self.primary.wait_is_text_available ():
            text = self.primary.wait_for_text ()
            is_text = not (text.startswith ("http") and not ' ' in text.strip())
            if text != self.cur_contents and is_text:
                return True
        return False

    def get_text_contents (self):
        """
        A wrapper around get_contents() and has_text_contents()
        """
        get_clipboard = self.application.config.get ('get_clipboard')
        if get_clipboard and self.has_text_contents ():
            text = self.primary.wait_for_text ()
            self.cur_contents = self.primary.wait_for_text ()
            return text

    def has_url_contents (self):
        """
        Check whether the primary clipboard has a new valid url available.
        """
        if self.primary.wait_is_text_available ():
            text = self.primary.wait_for_text ()
            if text != self.cur_contents and text.startswith ("http"):
                return True
        return False

    def get_url_contents (self):
        """
        A wrapper around get_contents() and has_url_contents()
        """
        get_clipboard = self.application.config.get ('get_clipboard')
        if get_clipboard and self.has_url_contents ():
            text = self.primary.wait_for_text ()
            self.cur_contents = text
            return text

    def set_contents (self, contents, force=False):
        """
        Set the contents of the CLIPBOARD clipboard
        only if the 'set_clipboard' is on or force is True.
        """

        if force or self.application.config.get ('set_clipboard'):
            self.cur_contents = contents
            self.primary.set_text (contents)
            self.clipboard.set_text (contents)

class Application (dbus.service.Object):
    """
    An object for managing a FreeSpeak application instance.
    WARNING: You should NOT create directly an application, please take a look at
    the get_instance() function to ensure the Application singleton.
    """

    def __init__ (self, bus, path, name):
        dbus.service.Object.__init__ (self, bus, path, name)

        self.globalkeybinding = None
        self.translators_path = None
        self.icons_path = None
        self.icon_theme = None
        self.clipboard = None
        self.main_window = None
        self.config = None
        self.translators_manager = None

        self.setup_l10n ()
        self.setup_exception_dialog ()
        self.setup_config ()
        self.setup_paths ()
        self.setup_icons ()
        self.setup_translators_manager ()
        self.setup_clipboard ()
        self.setup_style ()
        self.setup_globalkeybinding ()

        self.running = False
        self.gtkmain = False

    def setup_exception_dialog (self):
        """
        Setup a Python-wide exception hook
        """
        # FIXME: must take care if another excepthook had been installed
        sys.excepthook = exception_dialog.exception_hook

    @staticmethod
    def setup_l10n ():
        """
        Install the _ gettext function
        """
        # FIXME: must take care if it has been already called then we're
        #       going to override the _
        gettext.install (defs.GETTEXT_PACKAGE, unicode=True)

    def setup_config (self):
        """
        Create a configuration object
        """
        self.config = Config ()

    def setup_paths (self):
        """
        Setup common paths used for finding FreeSpeak resources
        """
        self.icons_path = os.path.join (defs.DATA_DIR, defs.PACKAGE, 'art')
        self.translators_path = os.path.dirname (freespeak.translators.__file__)

    def setup_icons (self):
        """
        Setup the GTK+ icon theme, adding the path for FreeSpeak art.
        Set the default icon for all windows.
        """
        self.icon_theme = gtk.icon_theme_get_default ()
        self.icon_theme.append_search_path (self.icons_path)
        # FIXME: must take care if the application was created from another
        #       application.
        window_icon = self.icon_theme.load_icon (defs.PACKAGE, 64, 0)
        gtk.window_set_default_icon (window_icon)

    def setup_translators_manager (self):
        """
        Create a TranslatorsManager instance for managing translators/translating engines.
        """
        self.translators_manager = TranslatorsManager (self)

    def setup_clipboard (self):
        """
        Create a ClipboardController instance for managing the clipboard
        """
        self.clipboard = ClipboardController (self)

    def setup_style (self):
        """
        Tweak the GTK+ widgets style
        """
        style.setup_rc ()

    def setup_globalkeybinding (self):
        """
        Create GlobalKeyBinding for the 'key_binding' setting
        """
        self.globalkeybinding = GlobalKeyBinding (self, "key_binding")

    @dbus.service.method ("de.berlios.FreeSpeak",
                          in_signature='', out_signature='b')
    def is_running (self):
        """
        Returns True whether the application is running, False otherwise.
        """
        return self.running

    @dbus.service.method ("de.berlios.FreeSpeak",
                          in_signature='a{sv}asib', out_signature='b')
    def start (self, options=None, args=None, timestamp=None, show_main_window=True):
        """
        Start the application in blocking mode.
        If the application is already running, the main window will be presented
        to the user and the function will return.
        """
        if self.running:
            if not timestamp:
                timestamp = int (time.time ())
            self.main_window.present_with_time (timestamp)
            return False

        gtk.gdk.threads_init()

        self.main_window = MainWindow (self)
        if show_main_window:
            self.main_window.show ()

        self.globalkeybinding.grab ()
        self.globalkeybinding.start ()

        self.running = True
        return True

    @dbus.service.method ("de.berlios.FreeSpeak",
                          in_signature='', out_signature='')
    def stop (self):
        """
        Stop the application from running.
        """
        if self.running:
            self.globalkeybinding.stop ()
            self.main_window.destroy ()
            self.running = False
            self.stopped ()

    @dbus.service.method ("de.berlios.FreeSpeak",
                          in_signature='i', out_signature='b')
    def open_translation (self, type):
        return self.main_window.open_translation (type)

    @dbus.service.signal ("de.berlios.FreeSpeak",
                          signature="")
    def stopped (self):
        """
        Signal the application has been stopped
        """
        pass

    @dbus.service.signal ("de.berlios.FreeSpeak",
                          signature="")
    def closed (self):
        """
        Signal the application has been closed but not stopped
        """
        pass

global bus

def get_proxy ():
    bus_object = bus.get_object ("de.berlios.FreeSpeak", "/")
    return dbus.Interface (bus_object, "de.berlios.FreeSpeak")

def get_instance ():
    """
    Get the DBUS instance of the application.
    de.berlios.FreeSpeak at path / with interface de.berlios.FreeSpeak
    """
    dbus.mainloop.glib.DBusGMainLoop (set_as_default=True)
    global bus
    bus = dbus.SessionBus ()
    request = bus.request_name ("de.berlios.FreeSpeak",
                                dbus.bus.NAME_FLAG_DO_NOT_QUEUE)
    if request != dbus.bus.REQUEST_NAME_REPLY_EXISTS:
        return Application (bus, '/', "de.berlios.FreeSpeak")

    return get_proxy ()

__all__ = ['get_proxy', 'get_instance']
