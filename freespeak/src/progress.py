"""
    progress.py
    Sun Sep 04 17:06:17 2005
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

import gtk, thread

class Progress(gtk.HBox):
    def __init__(self):
        gtk.HBox.__init__(self)
        self.w_label = gtk.Label(_("Ready"))
        self.w_progress = gtk.ProgressBar()
        self.pack_start(self.w_label, expand=False, fill=True)
        self.pack_start(gtk.Label(""), expand=True, fill=True)
        self.pack_start(self.w_progress, expand=False, fill=False)
        self.step_text = [ _("Ready"), _("Building query"),
                           _("Downloading translation"),
                           _("Parsing translation"),
                           _("Setting right encoding"), _("Completed")]
        self.set_border_width(4)
        
    def set_step(self, step):
        self.w_label.set_text(self.step_text[step])
        self.w_progress.set_fraction(step/5.0)
