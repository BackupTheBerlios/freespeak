"""
    trayicon.py
    Sun Jun 14 14:18:52 2005
    Copyright  2005 Italian Python User Group
    http://www.italianpug.org
   
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

import gtk, os, sys
try:
    from egg import trayicon
except:
    import trayicon

class Trayicon(trayicon.TrayIcon):
    def __init__(self, parent):
        trayicon.TrayIcon.__init__(self, "FreeSpeak")
        w_event = gtk.EventBox( )
        w_icon = gtk.Image( )
        w_icon.set_from_file(os.path.join(parent.icons, 'freespeak-16x16.png')) 

        w_event.set_events( gtk.gdk.BUTTON_PRESS_MASK | 
                              gtk.gdk.POINTER_MOTION_MASK | 
                              gtk.gdk.POINTER_MOTION_HINT_MASK |
                              gtk.gdk.CONFIGURE )
        
        w_event.add(w_icon);
        
        self.w_menu = gtk.Menu()

        self.w_show = gtk.CheckMenuItem(_("Show Window"))
        self.w_show.set_active(True)
        self.w_show.connect("toggled", self.on_show)

        self.w_menu.add(self.w_show)

        self.w_menu.add(gtk.SeparatorMenuItem())

        self.w_quit = gtk.ImageMenuItem(gtk.STOCK_QUIT, _("Quit"))
        self.w_quit.connect("button_press_event", self.on_quit)

        self.w_menu.add(self.w_quit)
        
        self.w_menu.show_all()
        w_event.connect("button_press_event", self.on_button);
        self.w_parent = parent
        self.add(w_event)
        self.w_tooltips = gtk.Tooltips()
        self.w_tooltips.set_tip(self, "FreeSpeak 0.1.1")
        self.w_tooltips.enable()
        self.show_all()

    def get_window(self):
        if self.w_parent.is_reduced:
            return self.w_parent.reduced
        else:
            return self.w_parent
            
    def wnd_hide(self):
        self.w_show.set_active(False)
        self.get_window().hide_all()
        
    def wnd_show(self):
        self.w_show.set_active(True)
        self.get_window().show_all()
        
    def show_hide(self):
        if self.get_window().get_property('visible'): self.wnd_hide()
        else: self.wnd_show()
        
    # Events
        
    def on_button(self, w, event):
        self.get_window()
        if event.button == 1:
            self.show_hide()
        elif event.button == 3:
            self.w_menu.popup(None, None, None, 0, event.time)
    
    def on_show(self, w):
        self.show_hide()

    def on_quit(self, w, event):
        if event.button == 1:
            gtk.main_quit()
