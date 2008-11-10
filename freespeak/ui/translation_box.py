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

        iter = model.append (['(none)', None])
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
        label = gtk.Label ("T_ranslator:")
        label.set_use_underline (True)
        label.show ()
        self.pack_start (label, False)
        
        combo = TranslatorCombo (self.application, self.translation.capability)
        combo.connect ('changed', self.on_translator_changed)
        combo.show ()
        self.pack_start (combo)

        label.set_mnemonic_widget (combo)

    def setup_from (self):
        label = gtk.Label ("_From:")
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
        label = gtk.Label ("T_o:")
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


