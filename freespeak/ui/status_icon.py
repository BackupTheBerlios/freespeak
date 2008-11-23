# FreeSpeak - a GUI frontend to online translator engines
# freespeak/ui/status_icon.py - this file is part of FreeSpeak
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

import gtk

class StatusIcon (gtk.StatusIcon):
    def __init__ (self, window):
        gtk.StatusIcon.__init__ (self)
        self.window = window

        self.set_from_icon_name ('freespeak')

        self.connect ('activate', self.on_activate)
        self.connect ('popup-menu', self.on_popup_menu)

    def on_activate (self, *args):
        if self.window.is_active ():
            self.tray ()
        else:
            self.untray ()

    def on_popup_menu (self, status_icon, button, activate_time):
        menu = gtk.Menu ()
        menu.set_accel_group (self.window.accel_group)

        item = self.window.action_group.get_action("Text").create_menu_item ()
        menu.append (item)
        item = self.window.action_group.get_action("Web").create_menu_item ()
        menu.append (item)
        item = gtk.SeparatorMenuItem ()
        item.show ()
        menu.append (item)
        item = self.window.action_group.get_action("Preferences").create_menu_item ()
        menu.append (item)
        item = self.window.action_group.get_action("About").create_menu_item ()
        menu.append (item)
        item = gtk.SeparatorMenuItem ()
        item.show ()
        menu.append (item)
        item = self.window.action_group.get_action("Quit").create_menu_item ()
        menu.append (item)
        menu.popup (None, None, gtk.status_icon_position_menu,
                    button, activate_time, status_icon)
        
    def tray (self):
        self.window.set_skip_taskbar_hint (True)
        self.window.iconify ()

    def untray (self):
        self.window.present ()
        self.window.set_skip_taskbar_hint (False)
