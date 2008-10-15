import glob
import os
import imp

from freespeak import utils
from freespeak.translation import TextTranslationRequest, WebTranslationRequest

class BaseTranslator (object):
    name = ""
    capabilities = ()

    def get_name (self):
        return self.name

    def translate (self, request):
        if isinstance (request, TextTranslationRequest):
            return self.translate_text (request)
        elif isinstance (request, WebTranslationRequest):
            return self.translate_web (request)
        else:
            raise RuntimeError ("Unknown translation request: %s" % str (request))

    def get_language_table (self):
        raise NotImplementedError ()

    def translate_text (self, request):
        raise NotImplementedError ()

    def translate_web (self, request):
        raise NotImplementedError ()

    def __cmp__ (self, other):
        if not other or self.name < other.name:
            return -1
        elif self.name > other.name:
            return 1
        return 0

class TranslatorsManager (set):
    def __init__ (self, application):
        set.__init__ (self)
        self.application = application

        files = glob.glob (os.path.join (self.application.translators_path, "*.py"))
        for fname in files:
            self.load_translator_from_file (fname)

    def load_translator_from_file (self, fname):
        # 1. Split the path and get the latest part of it
        # 2. Split the extension and get the name without .py
        mname = os.path.splitext(os.path.split(fname)[1])[0]
        return self.load_translator (mname)

    def load_translator (self, mname):
        if mname == '__init__':
            return
        info = imp.find_module (mname, [self.application.translators_path])
        module = imp.load_module (mname, *info)
        if not module in self:
            self.add (module.Translator ())
            return module

    def get_default (self):
        name = self.application.config.get ("translator", "default")
        if name:
            for translator in self:
                if translator.name == name:
                    return translator

__all__ = ['BaseTranslator', 'TranslatorsManager']
