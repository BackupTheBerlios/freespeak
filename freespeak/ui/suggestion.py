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
import freespeak.utils as utils
import freespeak.ui.utils as uiutils
from freespeak.status import *

class SuggestionsTreeView (gtk.TreeView):
    def __init__ (self):
        self.model = gtk.ListStore (str, gtk.gdk.Pixbuf, str, str, str)
        gtk.TreeView.__init__ (self, self.model)

        self.setup_options ()
        self.setup_columns ()

    def setup_options (self):
        self.set_rules_hint (True)

    def setup_columns (self):
        renderer = gtk.CellRendererText ()
        column = gtk.TreeViewColumn (_("Translation"), renderer, text=0)
        self.append_column (column)

        renderer = gtk.CellRendererPixbuf ()
        column = gtk.TreeViewColumn (_("Image"), renderer, pixbuf=1)
        self.append_column (column)

        renderer = gtk.CellRendererText ()
        column = gtk.TreeViewColumn (_("Application"), renderer, text=2)
        self.append_column (column)

        renderer = gtk.CellRendererText ()
        column = gtk.TreeViewColumn (_("Original"), renderer, text=3)
        self.append_column (column)

        renderer = gtk.CellRendererText ()
        column = gtk.TreeViewColumn (_("Project URL"), renderer, text=4)
        self.append_column (column)

class TranslationSuggestions (BaseUITranslation):
    capability = TranslationSuggestionsRequest

    def setup_ui (self):
        hbox = gtk.HBox (spacing=6)
        label = gtk.Label (_("Suggest"))
        label.show ()
        hbox.pack_start (label, False)

        self.entry = gtk.Entry ()
        self.entry.show ()
        hbox.pack_start (self.entry)
        
        hbox.show ()
        self.pack_start (hbox, False)

        self.suggestions = SuggestionsTreeView ()
        self.suggestions.show ()
        scrolled = uiutils.ScrolledWindow (self.suggestions)
        scrolled.set_shadow_type (gtk.SHADOW_NONE)
        scrolled.show ()

        self.pack_start (scrolled)

    def setup_clipboard (self):
        contents = self.application.clipboard.get_contents ()
        if contents is not None:
            self.entry.set_text (contents)

    def create_request (self):
        return TranslationSuggestionsRequest (self.entry.get_text ())

    @utils.syncronized
    def update_status (self, status):
        BaseUITranslation.update_status (self, status)
        if isinstance (status, StatusSuggestionComplete):
            self.suggestions.modify_base (gtk.STATE_NORMAL, self.DESTINATION_COLOR)
            model = self.suggestions.get_model ()
            for suggestion_result in status.result:
                model.append (suggestion_result)

__all__ = ['TranslationSuggestions']
