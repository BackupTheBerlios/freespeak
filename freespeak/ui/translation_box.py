# FreeSpeak - a GUI frontend to online translator engines
# freespeak/ui/translation_box.py - this file is part of FreeSpeak
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

from freespeak import utils

class TranslatorCombo (gtk.ComboBox):
    COL_TRANSLATOR_TEXT = 0
    COL_TRANSLATOR_TRANSLATOR = 1

    def __init__ (self, application, capability=None):
        gtk.ComboBox.__init__ (self)
        self.application = application

        model = gtk.ListStore (str, object)
        self.set_model (model)
        default_translator = self.application.translators_manager.get_default ()
        default_iter = None

        iter = model.append ([_("(none)"), None])
        self.set_active_iter (iter)
        for translator in sorted (self.application.translators_manager):
            if not capability or capability in translator.capabilities:
                iter = model.append ([translator.get_name (), translator])
                if translator == default_translator:
                    default_iter = iter

        if default_iter:
            self.set_active_iter (default_iter)

        cell = gtk.CellRendererText ()
        self.pack_start (cell)
        self.add_attribute (cell, 'text', self.COL_TRANSLATOR_TEXT)

    def get_active_translator (self):
        iter = self.get_active_iter ()
        if iter:
            translator = self.get_model().get_value (iter, self.COL_TRANSLATOR_TRANSLATOR)
            return translator

class TranslationBox (gtk.HBox):
    COL_FROM_TEXT = 0
    COL_FROM_LANG = 1
    COL_TO_TEXT = 0
    COL_TO_LANG = 1

    def __init__ (self, application, translation):
        gtk.HBox.__init__ (self, spacing=12)
        self.application = application
        self.translation = translation

        self.setup_translator ()
        self.setup_from ()
        self.setup_to ()

    def setup_translator (self):
        label = gtk.Label (_("T_ranslator:"))
        label.set_use_underline (True)
        label.show ()
        self.pack_start (label, False)
        
        combo = TranslatorCombo (self.application, self.translation.capability)
        combo.connect ('changed', self.on_translator_changed)
        combo.show ()
        self.pack_start (combo)

        label.set_mnemonic_widget (combo)

    def setup_from (self):
        label = gtk.Label (_("_From:"))
        label.set_use_underline (True)
        label.show ()
        self.pack_start (label, False)
        
        self.from_combo = gtk.ComboBox ()
        self.from_combo.set_sensitive (False)
        cell = gtk.CellRendererText ()
        self.from_combo.pack_start (cell)
        self.from_combo.add_attribute (cell, 'text', self.COL_FROM_TEXT)
        self.from_combo.connect ('changed', self.on_from_changed)
        self.pack_start (self.from_combo)
        self.from_combo.show ()

        label.set_mnemonic_widget (self.from_combo)

    def setup_to (self):
        label = gtk.Label (_("T_o:"))
        label.set_use_underline (True)
        label.show ()
        self.pack_start (label, False)
        
        self.to_combo = gtk.ComboBox ()
        self.to_combo.set_sensitive (False)
        cell = gtk.CellRendererText ()
        self.to_combo.pack_start (cell)
        self.to_combo.add_attribute (cell, 'text', self.COL_TO_TEXT)
        self.to_combo.connect ('changed', self.on_to_changed)
        self.pack_start (self.to_combo)
        self.to_combo.show ()

        label.set_mnemonic_widget (self.to_combo)

    def update_from_langs (self, langs):
        if not langs:
            self.from_combo.set_sensitive (False)
            return

        model = gtk.ListStore (str, object)
        for lang in langs:
            model.append ([str (lang), lang])
        self.from_combo.set_model (model)
        self.from_combo.set_sensitive (True)

    def update_to_langs (self, langs):
        if not langs:
            self.to_combo.set_sensitive (False)
            return

        model = gtk.ListStore (str, object)
        for lang in langs:
            model.append ([str (lang), lang])
        self.to_combo.set_model (model)
        self.to_combo.set_sensitive (True)

    def set_from_lang (self, lang):
        model = self.from_combo.get_model ()
        for row in model:
            if row[self.COL_FROM_LANG] == lang:
                self.from_combo.set_active_iter (row.iter)
                return True

    def set_to_lang (self, lang):
        model = self.to_combo.get_model ()
        for row in model:
            if row[self.COL_TO_LANG] == lang:
                self.to_combo.set_active_iter (row.iter)
                return True

    def swap_langs (self):
        iter = self.to_combo.get_active_iter ()
        to_model = self.to_combo.get_model ()
        to_lang = to_model.get_value (iter, self.COL_TO_LANG)

        iter = self.from_combo.get_active_iter ()
        from_model = self.from_combo.get_model ()
        from_lang = from_model.get_value (iter, self.COL_FROM_LANG)

        if not self.set_from_lang (to_lang):
            self.from_combo.set_active (-1)
        if not self.set_to_lang (from_lang):
            self.to_combo.set_active (-1)

    # Events

    def on_translator_changed (self, combo):
        translator = combo.get_active_translator ()
        self.translation.set_translator (translator)

    def on_from_changed (self, combo):
        iter = combo.get_active_iter ()
        lang = combo.get_model().get_value (iter, self.COL_FROM_LANG)
        self.translation.set_from_lang (lang)

    def on_to_changed (self, combo):
        iter = combo.get_active_iter ()
        lang = combo.get_model().get_value (iter, self.COL_TO_LANG)
        self.translation.set_to_lang (lang)

__all__ = ['TranslationBox']


