"""
    settings.py
    Fri Jun 14 13:41:56 2004
    Copyright (C) 2005-2006-2007-2008  Luca Bruno <lethalman88@gmail.com>
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

import gtk
from freespeak import utils
import freespeak.ui.utils as uiutils
from freespeak.ui.translation_box import TranslatorCombo

class Settings(gtk.Dialog):
    @utils.syncronized
    def __init__(self, application):
        """
        FreeSpeak user preferences
        """
        gtk.Dialog.__init__ (self, _('Preferences'), application.main_window, 0,
                             (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        self.application = application

        self.set_border_width (6)
        self.set_modal (True)

        self.setup_layout ()
        self.setup_clipboard ()
        self.setup_translator ()

        self.connect ('response', self.on_response)
        self.show ()

    def setup_layout (self):
        self.vbox.set_spacing (6)

    def setup_clipboard (self):
        frame = uiutils.Frame(_('Clipboard preferences'))
        frame.show ()
        vbox = gtk.VBox (spacing=6)
        vbox.show ()

        self.w_clipboard_get = gtk.CheckButton (_("_Get text from clipboard automatically"))
        self.w_clipboard_get.set_active (self.application.config.getboolean ('clipboard', 'get'))
        self.w_clipboard_get.show ()
        vbox.pack_start(self.w_clipboard_get, False)

        self.w_clipboard_set = gtk.CheckButton (_("_Save translated text to clipboard"))
        self.w_clipboard_set.set_active (self.application.config.getboolean ('clipboard', 'set'))
        self.w_clipboard_set.show ()
        vbox.pack_start(self.w_clipboard_set, False)
        
        frame.add (vbox)
        frame.show ()
        self.vbox.pack_start (frame)

    def setup_translator (self):
        frame = uiutils.Frame (_("Translator preferences"))
        frame.show ()
        vbox = gtk.VBox (spacing=6)
        vbox.show ()
        
        hbox = gtk.HBox(spacing=4)
        hbox.show ()
        label = gtk.Label ("_Preferred Translator")
        label.set_use_underline (True)
        label.show ()
        hbox.pack_start (label, False)
        self.w_preferred_translator = TranslatorCombo (self.application)
        self.w_preferred_translator.show ()
        label.set_mnemonic_widget (self.w_preferred_translator)
        hbox.pack_start (self.w_preferred_translator)
        vbox.pack_start(hbox)
        
        frame.add (vbox)
        frame.show ()
        self.vbox.pack_start (frame)

    def on_response (self, dialog, response):
        self.application.config.set ('clipboard', 'get', self.w_clipboard_get.get_active ())
        self.application.config.set ('clipboard', 'set', self.w_clipboard_set.get_active ())
        translator = self.w_preferred_translator.get_active_translator ()
        self.application.config.set ('translator', 'default', translator.module_name)
        self.application.config.save ()
        self.destroy()
