# FreeSpeak - a GUI frontend to online translator engines
# freespeak/ui/about.py - this file is part of FreeSpeak
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
import gnome

class About (gtk.AboutDialog):
    def __init__ (self, application):
        gtk.AboutDialog.__init__ (self)
        self.application = application

        self.set_name ("FreeSpeak")
        self.set_version (application.version)
        self.set_comments (_("A free frontend to online translator engines")) 
        self.set_license ("""
        FreeSpeak is free software; you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation; either version 2 of the License, or
        (at your option) any later version.
        
        FreeSpeak is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU Library General Public License for more details.
        
        You should have received a copy of the GNU General Public License
        along with this program; if not, write to the Free Software
        Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
        """)
        gtk.about_dialog_set_url_hook (self.on_url, "")
        gtk.about_dialog_set_email_hook (self.on_url, "mailto:")
                          
        self.set_website_label ("http://home.gna.org/freespeak/")
        self.set_website ("http://home.gna.org/freespeak/")
        self.set_authors (["Luca Bruno\t<lethalman88@gmail.com>"])
        self.set_logo (self.application.icon_theme.load_icon ('freespeak', 64, 0))
        self.set_artists (["Coviello Giuseppe\t<immigrant@email.it>"])
        self.set_translator_credits ("Luca Bruno\t<lethalman88@gmail.com>")
                                     
        self.set_copyright ("Copyright (C) 2005-2008  Luca Bruno <lethalman88@gmail.com>")

        self.connect ('response', self.on_response)
        self.show_all()

    def on_url (self, w, url, data):
        gnome.url_show (data+url)

    def on_response (self, *w):
        self.destroy ()
