import threading

class TranslationRequest (object):
    def __init__ (self):
        self.from_lang = None
        self.to_lang = None

class TextTranslationRequest (object):
    def __init__ (self, text):
        TranslationRequest.__init__ (self)
        self.text = text

class WebTranslationRequest (TranslationRequest):
    def __init__ (self, url):
        TranslationRequest.__init__ (self)
        self.url = url

class BaseTranslation (threading.Thread):
    STATUS_STARTED = 0
    STATUS_PROGRESS = 1
    STATUS_COMPLETE = 2

    def __init__ (self, application, manager):
        self.application = application
        self.manager = manager
        self.translator = None
        self.status = None
        self.status_text = None
        self.setup ()

        self.manager.add_translation (self)

    def close (self):
        self.manager.remove_translation (self)

    def set_translator (self, translator):
        self.translator = translator
        self.language_table = self.translator.get_language_table ()
        self.update_from_langs (sorted (self.language_table.keys()))

    def set_from_lang (self, lang):
        self.from_lang = lang
        self.update_to_langs (sorted (self.language_table[self.from_lang]))

    def set_to_lang (self, lang):
        self.to_lang = lang
        self.update_can_translate (True)

    def run (self, request):
        request.from_lang = self.from_lang
        request.to_lang = self.to_lang
        self.update_status (Translation.STATUS_STARTED, _("Translation started"))
        for status in self.translator.translate (request):
            self.update_status (Translation.STATUS_PROGRESS, status)
        self.update_status (Translation.STATUS_COMPLETE, _("Translation complete"))

    # Virtual methods

    def setup (self):
        pass

    def update_from_langs (self, langs):
        raise NotImplementedError ()

    def update_to_langs (self, langs):
        raise NotImplementedError ()

    def update_can_translate (self, can_translate):
        raise NotImplementedError ()

    def update_status (self, status, status_text):
        raise NotImplementedError ()

__all__ = ['BaseTranslation', 'TranslationRequest', 'TextTranslationRequest', 'WebTranslationRequest']
