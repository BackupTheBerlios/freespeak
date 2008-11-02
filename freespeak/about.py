#     about.py
#     Sat Jul 16 14:44:37 2005
#     Copyright (C) 2005-2006-2007-2008  Luca Bruno <lethalman88@gmail.com>
#     http://www.italianpug.org
   
#     This program is free software; you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation; either version 2 of the License, or
#     (at your option) any later version.
    
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Library General Public License for more details.

#     You should have received a copy of the GNU General Public License
#     along with this program; if not, write to the Free Software
#     Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import gtk, gtk.gdk, os, sys, os.path
from freespeak import defs

class About(gtk.AboutDialog):
    def __init__(self, parent):
        gtk.AboutDialog.__init__(self)
        self.set_name("FreeSpeak")
        self.set_version(defs.VERSION)
        self.set_comments(_("A free frontend to online translator engines")) 
        self.set_license("""
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
        """)
        gtk.about_dialog_set_url_hook(self.on_url, None)
        gtk.about_dialog_set_email_hook(self.on_url, "mailto:")

        self.set_website_label("http://home.gna.org/freespeak/")
        self.set_website("http://home.gna.org/freespeak/")
        self.set_authors(["Lethalman \n\tMail <lethalman88@gmail.com>",
                          "Coviello Giuseppe \n\tMail <immigrant@email.it>"+
                          "\n\tHomepage http://coviello.altervista.org"])
        if(os.path.isfile(os.path.join(parent.icons, "freespeak-64x64.png"))):
            self.set_logo(gtk.gdk.pixbuf_new_from_file(os.path.join(parent.icons,
                                                                    'freespeak-64x64.png')))  
        self.set_artists(["Coviello Giuseppe \n\tMail <immigrant@email.it>"+
                          "\n\tHomepage http://coviello.altervista.org"])
        self.set_translator_credits("Nederlands\n\tBoris De Vloed\n\tMail "+
                                     "<boris.de.vloed@telenet.be>\n"+
                                     "Italiano\n\tCoviello Giuseppe\n\t"+
                                     "Mail <immigrant@email.it>")
                                     
        self.set_copyright("Copyright (C) 2005 Luca Bruno <lethalman88@gmail.com> - "+
                           "http://www.italianpug.org")
        self.set_icon(parent.get_icon())
        self.show_all()

    def on_url(self, w, url, data):
        if not data:
            data = ""
        try:
            import gnome.ui
            gnome.ui.url_show_on_screen(data+url, w.get_screen())
        except:
            pass

