import threading

class BaseTranslation (threading.Thread):
    STATUS_STARTED = 0
    STATUS_PROGRESS = 1
    STATUS_COMPLETE = 2

    def __init__ (self, application):
        self.application = application
        self.translator = None
        self.status = None
        self.status_text = None
        self.setup ()

    def set_translator (self, translator):
        self.translator = translator
        self.language_table = self.translator.get_language_table ()
        self.update_from_langs (self.language_table.keys ())

    def set_from_lang (self, lang):
        self.from_lang = lang
        self.update_to_langs (self.language_table[self.from_lang])

    def set_to_lang (self, lang):
        self.to_lang = lang

    def run (self, data):
        self.update_status (Translation.STATUS_STARTED, _("Translation started"))
        for status in self.translator.translate (self.from_lang, self.to_lang, data):
            self.update_status (Translation.STATUS_PROGRESS, status)
        self.update_status (Translation.STATUS_COMPLETE, _("Translation complete"))

    # Virtual methods

    def setup (self):
        pass

    def update_from_langs (self, langs):
        raise NotImplementedError ()

    def update_to_langs (self, langs):
        raise NotImplementedError ()

    def update_status (self, status, status_text):
        raise NotImplementedError ()

__all__ = ['BaseTranslation']
