# FreeSpeak - a GUI frontend to online translator engines
# freespeak/ui/status_icon.py
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
Tray icon support for FreeSpeak
"""

import gtk

class StatusIcon (gtk.StatusIcon):
    """
    A FreeDesktop compliant status icon including a popup menu
    """
    ui_string = """<ui>
        <popup>
            <menuitem action="Text" />
            <menuitem action="Web" />
            <menuitem action="Suggestions" />
            <separator />
            <menuitem action="Preferences" />
            <menuitem action="Contents" />
            <menuitem action="About" />
            <separator />
            <menuitem action="Quit" />
        </popup>
    </ui>"""

    def __init__ (self, window):
        gtk.StatusIcon.__init__ (self)
        self.window = window

        self.set_from_icon_name ('freespeak')

        self.setup_menu ()

        self.connect ('activate', self.on_activate)
        self.connect ('popup-menu', self.on_popup_menu)

    def setup_menu (self):
        """
        Create a popup menu when the user right clicks the tray icon
        """
        # Re-creating actions from main window is an hack because it's
        # impossible to remove accelerators.
        # See GTK+ feature request:
        # http://bugzilla.gnome.org/show_bug.cgi?id=516425
        self.action_group = gtk.ActionGroup ('TrayActions')
        actions = (
            ('Text', None, _('_Text'), "",
             _('New translation'), self.on_new),

            ('Web', None, _('We_b'), "",
             _('New web page translation'), self.on_new),

            ('Suggestions', None, _('_Suggestions'), "",
             _('New translation suggestions'), self.on_new),

            ('Preferences', gtk.STOCK_PREFERENCES, None, "",
             _('FreeSpeak preferences'), self.window.on_settings),

            ('Contents', gtk.STOCK_HELP, _("_Contents"), "",
             None, self.window.on_contents),

            ('About', gtk.STOCK_ABOUT, None, "",
             _('About FreeSpeak'), self.window.on_about),

            ('Quit', gtk.STOCK_QUIT, None, "",
             _('Quit FreeSpeak'), self.window.on_quit),
            )
        self.action_group.add_actions (actions)
        self.ui = gtk.UIManager ()
        self.ui.insert_action_group (self.action_group, 0)
        self.ui.add_ui_from_string (self.ui_string)
        self.menu = self.ui.get_widget ("/popup")

        action = self.action_group.get_action ("Text")
        action.set_property ('icon-name', 'text-x-generic')
        action = self.action_group.get_action ("Web")
        action.set_property ('icon-name', 'text-html')
        action = self.action_group.get_action ("Suggestions")
        action.set_property ('icon-name', 'package-x-generic')


    # Events

    def on_activate (self, *args):
        """
        Called when the icon is clicked. This will raise the window.
        """
        if self.window.is_active ():
            self.tray ()
        else:
            self.untray ()

    def on_popup_menu (self, status_icon, button, activate_time):
        """
        Called when the user right clicks the icon
        """
        self.menu.popup (None, None, gtk.status_icon_position_menu,
                         button, activate_time, status_icon)
        
    def on_new (self, w):
        """
        Start a new translation and switch to the latest opened tab
        in the notebook
        """
        self.window.on_new (w)
        self.window.manager.switch_to_latest ()

    def tray (self):
        """
        Method for traying the window
        """
        self.window.set_skip_taskbar_hint (True)
        self.window.hide ()

    def untray (self):
        """
        Method for untraying the window
        """
        self.window.present ()
        self.window.set_skip_taskbar_hint (False)
