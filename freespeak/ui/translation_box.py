import gtk

from freespeak import utils

class TranslationBox (gtk.HBox):
    COL_TRANSLATOR_TEXT = 0
    COL_TRANSLATOR_TRANSLATOR = 1
    COL_FROM_TEXT = 0
    COL_FROM_LANG = 1
    COL_TO_TEXT = 0
    COL_TO_LANG = 1

    def __init__ (self, application, translation):
        gtk.HBox.__init__ (self, 6)
        self.application = application
        self.translation = translation

        self.setup_translator ()
        self.setup_from ()
        self.setup_to ()

    def setup_translator (self):
        label = utils.label_new_with_mnemonic (_("T_ranslator:"))
        label.show ()
        self.pack_start (label, False)
        
        combo = gtk.ComboBox ()
        model = gtk.ListStore (str, object)
        default_translator = self.application.translators_manager.get_default ()
        default_iter = None

        for translator in self.application.translators_manager:
            iter = model.append ([translator.get_name (), translator])
            if translator == default_translator:
                default_iter = iter

        combo.set_model (model)
        if default_iter:
            combo.set_active_iter (default_iter)

        cell = gtk.CellRendererText ()
        combo.pack_start (cell)
        combo.add_attribute (cell, 'text', self.COL_TRANSLATOR_TEXT)
        combo.connect ('changed', self.on_translator_changed)
        self.pack_start (combo)
        combo.show ()

    def setup_from (self):
        label = utils.label_new_with_mnemonic (_("_From:"))
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

    def setup_to (self):
        label = utils.label_new_with_mnemonic (_("_To:"))
        label.show ()
        self.pack_start (label, False)
        
        self.to_combo = gtk.ComboBox ()
        self.to_combo.set_sensitive (False)
        cell = gtk.CellRendererText ()
        self.from_combo.pack_start (cell)
        self.from_combo.add_attribute (cell, 'text', self.COL_TO_TEXT)
        self.to_combo.connect ('changed', self.on_to_changed)
        self.pack_start (self.to_combo)
        self.to_combo.show ()

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
        iter = combo.get_active_iter ()
        translator = iter[self.COL_TRANSLATOR_TRANSLATOR]
        self.translation.set_translator (translator)

    def on_from_changed (self, combo):
        iter = combo.get_active_iter ()
        lang = iter[self.COL_FROM_LANG]
        self.translation.set_from_lang (lang)

    def on_to_changed (self, combo):
        iter = combo.get_active_iter ()
        lang = iter[self.COL_TO_LANG]
        self.translation.set_to_lang (lang)

__all__ = ['TranslationBox']


