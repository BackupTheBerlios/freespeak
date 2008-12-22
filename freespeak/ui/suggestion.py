# FreeSpeak - a GUI frontend to online translator engines
# freespeak/ui/suggestion.py
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
import gnome

from freespeak.translation import TranslationSuggestionsRequest
from freespeak.ui.translation import BaseUITranslation

import freespeak.utils as utils
import freespeak.ui.utils as uiutils
from freespeak.status import *
import pango

class SuggestionsTreeView (gtk.TreeView):
    COL_TRANSLATION = 0
    COL_ORIGINAL = 1
    COL_PIXBUF = 2
    COL_APPLICATION = 3
    COL_URL = 4

    ui_string = """<ui>
        <popup name="PopupMenu">
            <menuitem action="Copy" />
            <menuitem action="Open" />
        </popup>
    </ui>"""


    def __init__ (self, application):
        self.model = gtk.ListStore (str, str, gtk.gdk.Pixbuf, str, str)
        gtk.TreeView.__init__ (self, self.model)
        self.application = application

        self.setup_options ()
        self.setup_columns ()
        self.setup_menu ()

    def setup_options (self):
        self.set_rules_hint (True)
        self.set_reorderable (True)

    def setup_columns (self):
        renderer = gtk.CellRendererText ()
        attributes = pango.AttrList ()
        attributes.insert (pango.AttrWeight (pango.WEIGHT_BOLD, 0, -1))
        renderer.set_property ("attributes", attributes)
        column = gtk.TreeViewColumn (_("Translation"), renderer, text=self.COL_TRANSLATION)
        column.set_resizable (True)
        self.append_column (column)

        renderer = gtk.CellRendererText ()
        column = gtk.TreeViewColumn (_("Original"), renderer, text=self.COL_ORIGINAL)
        column.set_resizable (True)
        self.append_column (column)

        renderer = gtk.CellRendererPixbuf ()
        column = gtk.TreeViewColumn (_("Application"), None)
        column.pack_start (renderer, expand=False)
        column.add_attribute (renderer, 'pixbuf', self.COL_PIXBUF)
        renderer = gtk.CellRendererText ()
        column.pack_start (renderer)
        column.add_attribute (renderer, 'text', self.COL_APPLICATION)
        self.append_column (column)

    def setup_menu (self):
        self.action_group = gtk.ActionGroup ('PopupActions')
        actions = (
            ('Copy', gtk.STOCK_COPY, None, None,
             _('Copy the suggested translation'), self.on_copy),
            ('Open', gtk.STOCK_OPEN, _('_Open project page'), "<Control>w",
             _('Open the translation project web page'), self.on_open),
            )
        self.action_group.add_actions (actions)
        self.ui = gtk.UIManager ()
        self.ui.insert_action_group (self.action_group, 0)
        self.ui.add_ui_from_string (self.ui_string)
        self.menu = self.ui.get_widget ("/PopupMenu")
        self.connect ('button-press-event', self.on_button_press_event, self.menu)

    def on_button_press_event (self, tree, event, menu):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            result = self.get_path_at_pos (int (event.x), int (event.y))
            if result:
                self.path = result[0]
                menu.popup (None, None, None, event.button, event.time, None)
                return True

    def on_copy (self, action):
        iter = self.model.get_iter (self.path)
        if iter:
            translation = self.model.get_value (iter, self.COL_TRANSLATION)
            self.application.clipboard.set_contents (translation)

    def on_open (self, action):
        iter = self.model.get_iter (self.path)
        if iter:
            url = self.model.get_value (iter, self.COL_URL)
            gnome.url_show (url)

class TranslationSuggestions (BaseUITranslation):
    capability = TranslationSuggestionsRequest

    def entry_buttons (self):
        box = gtk.HBox (homogeneous=True)
        # Clear
        btn = uiutils.TinyButton (gtk.STOCK_CLEAR)
        btn.set_tooltip_text (_("Clear the phrase"))
        btn.connect ('clicked', self.on_tiny_clear)
        btn.show ()
        box.pack_start (btn)
        # Paste
        btn = uiutils.TinyButton (gtk.STOCK_PASTE)
        btn.set_tooltip_text (_("Paste the phrase from the clipboard"))
        btn.connect ('clicked', self.on_tiny_paste)
        btn.show ()
        box.pack_start (btn)
        box.show ()
        return box

    def setup_ui (self):
        self.can_translate = False

        hbox = gtk.HBox (spacing=6)
        label = gtk.Label (_("Suggest"))
        label.show ()
        hbox.pack_start (label, False)

        self.entry = gtk.Entry ()
        self.entry.connect ('changed', self.on_entry_changed)
        self.entry_activate_handler = self.entry.connect ('activate', lambda *args: self.translate_button.clicked ())
        self.entry.handler_block (self.entry_activate_handler)
        self.entry.show ()
        hbox.pack_start (self.entry)

        hbox.pack_start (self.entry_buttons (), False)
        
        hbox.show ()
        self.layout.pack_start (hbox, False)

        self.suggestions = SuggestionsTreeView (self.application)
        self.suggestions.show ()
        scrolled = uiutils.ScrolledWindow (self.suggestions)
        scrolled.set_shadow_type (gtk.SHADOW_NONE)
        scrolled.show ()

        self.layout.pack_start (scrolled)

    def setup_clipboard (self):
        contents = self.application.clipboard.get_contents ()
        if contents is not None:
            self.entry.set_text (contents)

    def create_request (self):
        return TranslationSuggestionsRequest (self.entry.get_text ())

    @utils.syncronized
    def update_can_translate (self, can_translate):
        self.can_translate = can_translate
        self.update_translate_button_sensitivity ()

    def update_translate_button_sensitivity (self):
        sensitivity = self.can_translate and bool (self.entry.get_text ())
        self.translate_button.set_sensitive (sensitivity)
        if sensitivity:
            self.entry.handler_unblock (self.entry_activate_handler)
        else:
            self.entry.handler_block (self.entry_activate_handler)

    @utils.syncronized
    def update_status (self, status):
        BaseUITranslation.update_status (self, status)
        if isinstance (status, StatusSuggestionComplete):
            self.suggestions.modify_base (gtk.STATE_NORMAL, self.DESTINATION_COLOR)
            model = self.suggestions.get_model ()
            model.clear ()
            for suggestion_result in status.result:
                model.append (suggestion_result)
                
    # Events

    def on_entry_changed (self, entry):
        self.update_translate_button_sensitivity ()

    def on_tiny_clear (self, button):
        self.entry.set_text ("")
        self.entry.grab_focus ()

    def on_tiny_paste (self, button):
        contents = self.application.clipboard.get_contents ()
        if contents is not None:
            self.entry.set_text (contents)

__all__ = ['TranslationSuggestions']
