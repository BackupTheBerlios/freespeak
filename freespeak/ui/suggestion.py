# FreeSpeak - a GUI frontend to online translator engines
# freespeak/ui/suggestion.py - this file is part of FreeSpeak
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

from freespeak.ui.translation import BaseUITranslation, TranslationSuggestionsRequest
import freespeak.ui.utils as uiutils

class TranslationSuggestions (BaseUITranslation):
    capability = TranslationSuggestionsRequest

    def setup_ui (self):
        hbox = gtk.HBox (spacing=6)
        label = gtk.Label ("Suggest")
        label.show ()
        hbox.pack_start (label, False)

        self.entry = gtk.Entry ()
        self.entry.show ()
        hbox.pack_start (self.entry)
        
        hbox.show ()
        self.pack_start (hbox, False)

        self.suggestions = gtk.VBox (spacing=6)
        self.suggestions.show ()
        viewport = gtk.Viewport ()
        viewport.add (self.suggestions)
        viewport.modify_bg (gtk.STATE_NORMAL, self.DESTINATION_COLOR)
        viewport.show ()
        scrolled = uiutils.ScrolledWindow (viewport)
        scrolled.set_shadow_type (gtk.SHADOW_NONE)
        scrolled.show ()
        self.pack_start (scrolled)

    def setup_clipboard (self):
        contents = self.application.clipboard.get_contents ()
        if contents is not None:
            self.entry.set_text (contents)

    def create_request (self):
        return TranslationSuggestionsRequest (self.entry.get_text ())

__all__ = ['TranslationSuggestions']
