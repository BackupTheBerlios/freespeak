# FreeSpeak - a GUI frontend to online translator engines
# freespeak/ui/main_window.py
#
## Copyright (C) 2005, 2006, 2007, 2008  Luca Bruno <lethalman88@gmail.com>
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

import os
import gtk
import gnome

from freespeak import defs
from freespeak.ui.manager import *
from freespeak.ui.translation import *
from freespeak.ui.suggestion import *
from freespeak.ui.settings import *
from freespeak.ui.status_icon import StatusIcon
from freespeak.ui.about import About

class MainWindow (gtk.Window):
    ui_string = """<ui>
        <menubar>
            <menu action="Translation">
                <menuitem action="Text" />
                <menuitem action="Web" />
                <menuitem action="Suggestions" />
                <separator />
                <menuitem action="Close" />
                <menuitem action="Quit" />
            </menu>
            <menu action="Edit">
                <menuitem action="Preferences" />
            </menu>
            <menu action="Help">
                <menuitem action="Contents" />
                <menuitem action="About" />
            </menu>
        </menubar>
        <toolbar>
            <toolitem action="Text" />
            <toolitem action="Web" />
            <toolitem action="Suggestions" />
            <separator />
            <toolitem action="Preferences" />
        </toolbar>
        <accelerator action="Text" />
        <accelerator action="Web" />
        <accelerator action="Suggestions" />
        <accelerator action="Preferences" />
        <accelerator action="Contents" />
        <accelerator action="Quit" />
        </ui>"""
                
    def __init__(self, application):
        gtk.Window.__init__ (self)
        self.application = application

        self.setup_clipboard ()
        self.setup_window ()
        self.setup_layout ()
        self.setup_status_icon ()

    def setup_status_icon (self):
        self.status_icon = StatusIcon (self)

    def setup_clipboard (self):
        self.clipboard = gtk.Clipboard()
        self.cur_clipboard = ''

    def setup_window (self):
        self.connect ('delete-event', self.on_delete_event)
        icon = self.application.icon_theme.load_icon (defs.PACKAGE, 64, 0)
        self.set_icon (icon)
        self.set_title ('FreeSpeak')
        self.set_default_size (500, 400)

    def setup_layout (self):
        self.layout = gtk.VBox ()

        self.action_group = gtk.ActionGroup ('WindowActions')
        actions = (
            ('Translation', None, _("Translation")),
            ('Edit', None, _("_Edit")),
            ('Help', None, _("_Help")),

            ('Text', gtk.STOCK_NEW, _('_Text'), "<Control>t",
             _('New translation'), self.on_new),

            ('Web', gtk.STOCK_NETWORK, _('We_b'), "<Control>b",
             _('New web page translation'), self.on_new),

            ('Suggestions', gtk.STOCK_SELECT_FONT, _('_Suggestions'), "<Control>s",
             _('New translation suggestions'), self.on_new),

            ('Preferences', gtk.STOCK_PREFERENCES, None,
             "<Control>p", _('FreeSpeak preferences'), self.on_settings),

            ('Close', gtk.STOCK_CLOSE, _("_Close this translation"), None,
             _("Close the active translation page"), self.on_close),

            ('Contents', gtk.STOCK_HELP, _("_Contents"),
             "F1", None, self.on_contents),

            ('About', gtk.STOCK_ABOUT, None, None,
             _('About FreeSpeak'), self.on_about),

            ('Quit', gtk.STOCK_QUIT, None, "<Control>q",
             _('Quit FreeSpeak'), self.on_quit),
            )
        self.action_group.add_actions (actions)
        self.ui = gtk.UIManager ()
        self.ui.insert_action_group (self.action_group, 0)
        self.ui.add_ui_from_string (self.ui_string)
        self.accel_group = self.ui.get_accel_group ()
        self.add_accel_group (self.accel_group)

        self.setup_menubar ()
        self.setup_toolbar ()
        self.setup_manager ()

        self.layout.show ()
        self.add (self.layout)

    def setup_menubar (self):
        self.menubar = self.ui.get_widget ("/menubar")
        self.menubar.show ()
        self.layout.pack_start (self.menubar, False)

    def setup_toolbar (self):
        self.toolbar = self.ui.get_widget ("/toolbar")
        self.toolbar.show ()
        self.layout.pack_start (self.toolbar, False)

    def setup_manager (self):
        self.manager = Manager (self.application)
        self.manager.show ()
        self.layout.pack_start (self.manager)

    def quit (self):
        self.application.stop ()
            
    # Events
        
    def on_new (self, w):
        """
        Open a new tab in the notebook and start a new translation
        """
        type = w.get_name()
        if type == 'Text':
            translation = TextTranslation (self.application, self.manager)
        elif type == 'Web':
            translation = WebTranslation (self.application, self.manager)
        elif type == 'Suggestions':
            translation = TranslationSuggestions (self.application, self.manager)
        self.present ()
                
    def on_settings(self, w):
        """
        FreeSpeak preferences
        """
        Settings (self.application)

    def on_close (self, w):
        """
        Close the active translation page
        """
        self.manager.close_current_translation ()
                
    def on_contents (self, w):
        """
        Help contents
        """
        gnome.url_show ("ghelp:freespeak")

    def on_about(self, w):
        """
        Open an AboutDialog for this software
        """
        About (self.application)
                          
    def on_quit (self, *w):
        """
        Quit the application
        """
        self.quit ()

    def on_delete_event (self, *w):
        """
        Put myself in the system tray
        """
        self.status_icon.tray ()
        return True
