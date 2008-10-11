class Translation (object):
    def __init__ (self, application):
        self.application = application

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
