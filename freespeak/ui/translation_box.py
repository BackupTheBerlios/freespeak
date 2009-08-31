# FreeSpeak - a GUI frontend to online translator engines
# freespeak/ui/translation_box.py
#
## Copyright (C) 2005, 2006, 2007, 2008, 2009  Luca Bruno <lethalman88@gmail.com>
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

"""
Classes for handling a complete box of widgets for running a translation
"""

import gtk

class ComboChangedSignal (object):
    """
    Wrapper for the 'changed' singla of a combobox.
    Do not really change to the user choice item.
    """

    def __init__ (self, combo, callback):
        self.combo = combo
        self.callback = callback
        self.signal = self.combo.connect ('changed', self.on_changed)
        self.active_iter = self.combo.get_active_iter ()
        self.blocked = False

    def block (self):
        """
        Soft-block the signal
        """
        self.blocked = True

    def unblock (self):
        """
        Soft-unblock the signal
        """
        self.blocked = False

    def on_changed (self, combo):
        """
        If blocked, save the selected iter.
        Otherwise, call the callback just like emitting the 'changed' signal
        and select the old active item.
        """
        if self.blocked:
            self.active_iter = self.combo.get_active_iter ()
        else:
            self.callback (combo)
            self.block ()
            self.combo.set_active_iter (self.active_iter)
            self.unblock ()

class TranslatorCombo (gtk.ComboBox):
    """
    ComboBox for the translators
    """
    COL_TEXT = 0
    COL_TRANSLATOR = 1
    COL_PIXBUF = 2

    def __init__ (self, application, capability=None):
        gtk.ComboBox.__init__ (self)
        self.application = application

        model = gtk.ListStore (str, object, gtk.gdk.Pixbuf)
        self.set_model (model)

        titer = model.append ([_("(none)"), None, None])
        self.set_active_iter (titer)
        for translator in sorted (self.application.translators_manager):
            if not capability or capability in translator.capabilities:
                try:
                    pixbuf = self.application.icon_theme.load_icon (translator.icon,
                                                                    16, 0)
                except:
                    pixbuf = None
                titer = model.append ([translator.get_name (),
                                      translator, pixbuf])

        cell = gtk.CellRendererPixbuf ()
        self.pack_start (cell, expand=False)
        self.add_attribute (cell, 'pixbuf', self.COL_PIXBUF)

        cell = gtk.CellRendererText ()
        self.pack_start (cell)
        self.add_attribute (cell, 'text', self.COL_TEXT)

    def get_active_translator (self):
        """
        Wrapper method to easily get the active selected translator
        """
        titer = self.get_active_iter ()
        if titer:
            translator = self.get_model().get_value (titer,
                                                     self.COL_TRANSLATOR)
            return translator

    def set_active_translator (self, translator):
        model = self.get_model ()
        for row in model:
            if row[self.COL_TRANSLATOR] == translator:
                self.set_active_iter (row.iter)
                break

class TranslationBox (gtk.HBox):
    """
    This horizontal box contains several combobox:
    - The translators
    - The source languages
    - The destination languages
    """
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
        """
        Setup the translator combo box
        """
        label = gtk.Label (_("T_ranslator:"))
        label.set_use_underline (True)
        label.show ()
        self.pack_start (label, False)
        
        self.translator_combo = TranslatorCombo (self.application,
                                                 self.translation.capability)
        signal = ComboChangedSignal (self.translator_combo,
                                     self.on_translator_changed)
        self.translator_combo_signal = signal
        self.translator_combo.show ()
        self.pack_start (self.translator_combo)

        label.set_mnemonic_widget (self.translator_combo)

    def setup_from (self):
        """
        Setup source languages
        """
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
        """
        Setup destination languages
        """
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
        """
        Externally used to notify the list of source languages have been changed
        """
        if not langs:
            self.from_combo.set_sensitive (False)
            return

        model = gtk.ListStore (str, object)
        for lang in langs:
            model.append ([str (lang), lang])
        self.from_combo.set_model (model)
        self.from_combo.set_sensitive (True)
        self.from_combo.set_active (-1)

    def update_to_langs (self, langs):
        """
        Externally used to notify the list of destination languages have
        been changed
        """
        if not langs:
            self.to_combo.set_sensitive (False)
            return

        model = gtk.ListStore (str, object)
        for lang in langs:
            model.append ([str (lang), lang])
        self.to_combo.set_model (model)
        self.to_combo.set_sensitive (True)
        self.to_combo.set_active (-1)

    def set_translator (self, translator):
        """
        Set the active translator in the combobox
        """
        model = self.translator_combo.get_model ()
        for row in model:
            if row[TranslatorCombo.COL_TRANSLATOR] == translator:
                self.translator_combo_signal.block ()
                self.translator_combo.set_active_iter (row.iter)
                self.translator_combo_signal.unblock ()
                return True

    def set_from_lang (self, lang):
        """
        Set the source language
        """
        model = self.from_combo.get_model ()
        for row in model:
            if row[self.COL_FROM_LANG] == lang:
                self.from_combo.set_active_iter (row.iter)
                return True

    def set_to_lang (self, lang):
        """
        Set the destination language
        """
        model = self.to_combo.get_model ()
        for row in model:
            if row[self.COL_TO_LANG] == lang:
                self.to_combo.set_active_iter (row.iter)
                return True

    def swap_langs (self):
        """
        Swap the two languages in the comboboxes when possible
        """
        titer = self.to_combo.get_active_iter ()
        to_model = self.to_combo.get_model ()
        to_lang = to_model.get_value (titer, self.COL_TO_LANG)

        titer = self.from_combo.get_active_iter ()
        from_model = self.from_combo.get_model ()
        from_lang = from_model.get_value (titer, self.COL_FROM_LANG)

        if not self.set_from_lang (to_lang):
            self.from_combo.set_active (-1)
        if not self.set_to_lang (from_lang):
            self.to_combo.set_active (-1)

    # Events

    def on_translator_changed (self, combo):
        """
        The user changed the translator. This will notify the translation
        to change the translator to the selected one.
        The user won't see any graphical change unless the translation
        notifies us the translator really changed.
        """
        translator = combo.get_active_translator ()
        self.translation.set_translator (translator)

    def on_from_changed (self, combo):
        """
        The source language has been changed by the user
        """
        titer = combo.get_active_iter ()
        if not titer:
            return
        lang = combo.get_model().get_value (titer, self.COL_FROM_LANG)
        self.translation.set_from_lang (lang)

    def on_to_changed (self, combo):
        """
        The destination language has been changed by the user
        """
        titer = combo.get_active_iter ()
        if not titer:
            return
        lang = combo.get_model().get_value (titer, self.COL_TO_LANG)
        self.translation.set_to_lang (lang)

__all__ = ['TranslationBox']


