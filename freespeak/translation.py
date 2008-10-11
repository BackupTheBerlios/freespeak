import threading

class Translation (threading.Thread):
    STATUS_STARTED = 0
    STATUS_PROGRESS = 1
    STATUS_COMPLETE = 2

    def __init__ (self, application):
        self.application = application
        self.translator = None
        self.status = None
        self.status_text = None

    def set_translator (self, translator):
        self.translator = translator
        self.language_table = self.translator.get_language_table ()
        self.update_from_langs (self.language_table.keys ())

    def set_from_lang (self, lang):
        self.from_lang = lang
        self.update_to_langs (self.language_table[self.from_lang])

    def set_to_lang (self, lang):
        self.to_lang = lang

    def update_from_langs (self, langs):
        raise NotImplementedError ()

    def update_to_langs (self, langs):
        raise NotImplementedError ()

    def update_status (self, status, status_text):
        raise NotImplementedError ()

    def run (self, data):
        self.update_status (Translation.STATUS_STARTED, _("Translation started"))
        for status in self.translator.translate (self.from_lang, self.to_lang, data):
            self.update_status (Translation.STATUS_PROGRESS, status)
        self.update_status (Translation.STATUS_COMPLETE, _("Translation complete"))

class TextTranslation (Translation):
    pass

class WebTranslation (Translation):
    pass

class TranslationFactory (object):
    TEXT = 0
    WEB = 0

    translation_classes = { TEXT: TextTranslation,
                            WEB: WebTranslation }

    def __init__ (self, application):
        self.application = application

    def __call__ (self, type=Factory.TEXT, module=None):
        if not module:
            module = self.application.config.get ('translator', 'preferred')

        klass = self.translation_classes[type]
        return klass (self.application)
