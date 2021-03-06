# FreeSpeak - a GUI frontend to online translator engines
# freespeak/ui/main_window.py
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
Classes for showing the main window of a FreeSpeak application
"""

import time
import gtk

from freespeak import defs
from freespeak.ui.manager import Manager
from freespeak.ui.intro import Intro
from freespeak.ui.translation import TextTranslation, WebTranslation
from freespeak.ui.suggestion import TranslationSuggestions
from freespeak.ui.settings import Settings
from freespeak.ui.about import About

class MainWindow (gtk.Window):
    """
    The GTK+ main window
    """

    ui_string = """<ui>
        <menubar>
            <menu action="Translation">
                <menuitem action="Text" />
                <menuitem action="Web" />
                <menuitem action="Suggestions" />
                <separator />
                <menuitem action="Close" />
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
        </ui>"""
                
    def __init__(self, application):
        gtk.Window.__init__ (self)
        self.application = application

        self.setup_window ()
        self.setup_layout ()

        self.application.globalkeybinding.connect ('activate',
                                                   self.on_keybinding_activate)

    def setup_window (self):
        """
        Setup the basics of the window, like title and something else
        """
        self.connect ('delete-event', self.on_delete_event)
        icon = self.application.icon_theme.load_icon (defs.PACKAGE, 64, 0)
        self.set_icon (icon)
        self.set_title ('FreeSpeak')

    def setup_layout (self):
        """
        Setup the layout and the window actions
        """
        self.layout = gtk.VBox ()

        self.action_group = gtk.ActionGroup ('WindowActions')
        actions = (
            ('Translation', None, _("Translation")),
            ('Edit', None, _("_Edit")),
            ('Help', None, _("_Help")),

            ('Text', None, _('_Text'), "<Control>t",
             _('New translation'), None),

            ('Web', None, _('We_b'), "<Control>b",
             _('New web page translation'), None),
            
            ('Suggestions', None, _('_Suggestions'),
             "<Control>s", _('New translation suggestions'), None),

            ('Preferences', gtk.STOCK_PREFERENCES, None,
             "<Control>p", _('FreeSpeak preferences'), self.on_settings),

            ('Close', gtk.STOCK_CLOSE, _("_Close this translation"), None,
             _("Close the active translation page"), self.on_close),

            ('Contents', gtk.STOCK_HELP, _("_Contents"),
             "F1", None, self.on_contents),

            ('About', gtk.STOCK_ABOUT, None, None,
             _('About FreeSpeak'), self.on_about),
            )
        self.action_group.add_actions (actions)
        self.application.configure_actions (self.action_group)
        self.ui = gtk.UIManager ()
        self.ui.insert_action_group (self.action_group, 0)
        self.ui.add_ui_from_string (self.ui_string)
        self.accel_group = self.ui.get_accel_group ()
        self.add_accel_group (self.accel_group)

        self.setup_menubar ()
        self.setup_toolbar ()
        self.setup_manager ()
        self.setup_intro ()

        self.layout.show ()
        self.add (self.layout)

    def setup_menubar (self):
        """
        Add the menubar
        """
        action = self.action_group.get_action ("Text")
        action.set_property ('icon-name', 'text-x-generic')
        action = self.action_group.get_action ("Web")
        action.set_property ('icon-name', 'text-html')
        action = self.action_group.get_action ("Suggestions")
        action.set_property ('icon-name', 'package-x-generic')
        self.menubar = self.ui.get_widget ("/menubar")
        self.menubar.show ()
        self.layout.pack_start (self.menubar, False)

    def setup_toolbar (self):
        """
        Add the toolbar
        """
        self.toolbar = self.ui.get_widget ("/toolbar")
        self.toolbar.show ()
        self.layout.pack_start (self.toolbar, False)

    def setup_manager (self):
        """
        Create the tabs manager
        """
        self.manager = Manager (self.application)
        self.manager.show ()
        self.layout.pack_start (self.manager)

    def setup_intro (self):
        """
        Create the introduction container
        """
        self.intro = Intro (self.application, self.manager)
        self.intro.show ()
        self.layout.pack_start (self.intro)

    def open_translation (self, type):
        """
        Open a new tab in the notebook and start a new translation
        """
        if type == self.application.TEXT_TRANSLATION:
            TextTranslation (self.application, self.manager)
        elif type == self.application.WEB_TRANSLATION:
            WebTranslation (self.application, self.manager)
        elif type == self.application.TRANSLATION_SUGGESTIONS:
            TranslationSuggestions (self.application, self.manager)
        else:
            return False

        self.present ()
        return True

    # Events
        
    def on_keybinding_activate (self, keybinding):
        """
        Global keybinding has been activated
        """
        if self.application.clipboard.has_text_contents ():
            TextTranslation (self.application, self.manager)
        elif self.application.clipboard.has_url_contents ():
            WebTranslation (self.application, self.manager)
        else:
            return
        self.manager.switch_to_latest ()
        timestamp = int (time.time ())
        self.present_with_time (timestamp)

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
        gtk.show_uri (self.window.get_screen(), "ghelp:freespeak", 0)

    def on_about (self, w):
        """
        Open an AboutDialog for this software
        """
        About (self.application)
                          
    def on_delete_event (self, *w):
        """
        Let applications decide
        """
        self.application.closed ()
        return True
