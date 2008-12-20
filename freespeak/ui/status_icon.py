# FreeSpeak - a GUI frontend to online translator engines
# freespeak/ui/status_icon.py
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

import gtk

class StatusIcon (gtk.StatusIcon):
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
        # Re-creating actions from main window is an hack because it's impossible to remove accelerators
        self.action_group = gtk.ActionGroup ('TrayActions')
        actions = (
            ('Text', gtk.STOCK_NEW, _('_Text'), "",
             _('New translation'), self.on_new),

            ('Web', gtk.STOCK_NETWORK, _('We_b'), "",
             _('New web page translation'), self.on_new),

            ('Suggestions', gtk.STOCK_SELECT_FONT, _('_Suggestions'), "",
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

    def on_activate (self, *args):
        if self.window.is_active ():
            self.tray ()
        else:
            self.untray ()

    def on_popup_menu (self, status_icon, button, activate_time):
        self.menu.popup (None, None, gtk.status_icon_position_menu,
                         button, activate_time, status_icon)
        
    def on_new (self, w):
        """
        Start a new translation and switch to the latest opened tbat in the notebook
        """
        self.window.on_new (w)
        self.window.manager.switch_to_latest ()

    def tray (self):
        self.window.set_skip_taskbar_hint (True)
        self.window.iconify ()

    def untray (self):
        self.window.present ()
        self.window.set_skip_taskbar_hint (False)
