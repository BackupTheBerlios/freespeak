import gtk, os

class BaseTranslation:
    def on_module(self, widget):
        """
        Get the Translator class then insert from languages using the
        language table and set w_from widget sensitive.
        """
        itr = self.w_module.get_active_iter()
        self.translator = self.w_module.get_model().get_value(itr,
                                                              1)(self._parent)
        from_langs = []
        from_model = gtk.ListStore(str)
        for lang in self.translator.language_table:
            if lang["from"] not in from_langs:
                from_langs.append(lang["from"])
                from_model.append([lang["from"]])
        if self.translator.language_table:
            self.w_from.set_model(from_model)
            self.w_from.set_sensitive(1)
        if self.tabbed:
            if self._parent.custom_tab_name == False:
                self._parent.tab_name = widget.get_active_text()
                self._parent.set_label_tab()
            self._parent.tab_image.set_from_file(os.path.join(
                self._parent._parent.icons,
                self.translator.icon_file))
    
    def on_from(self, widget):
        """
        Get the languages which can be translated from the selected language
        and set w_to widget sensitive.
        """
        self.translator.from_lang = widget.get_active_text()
        to_model = gtk.ListStore(str)
        for lang in self.translator.language_table:
            if lang["from"] == widget.get_active_text():
                to_model.append([lang["to"]])

        self.w_to.set_model(to_model)
        if len(to_model) == 1:
            self.w_to.set_active(0)
        self.w_to.set_sensitive(1)
    
    def on_to(self, widget):
        """
        Translation ready to be started
        """
        self.translator.to_lang = widget.get_active_text()
        self.w_translate.set_sensitive(1)
        try:
            self.w_browser.set_sensitive(1)
        except:
            pass

__all__ = ['BaseTranslation']
