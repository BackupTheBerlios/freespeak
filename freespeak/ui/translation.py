import gtk

from freespeak.translation import *
from translation_box import *

class BaseUITranslation (gtk.VBox, BaseTranslation):
    def __init__ (self, *args):
        BaseTranslation.__init__ (self, *args)
        gtk.VBox.__init__ (self, 6)

    def setup (self):
        self.setup_translation_box ()
        self.setup_ui ()

    def setup_translation_box (self):
        self.translation_box = TranslationBox (self.application, self)

    def setup_ui (self):
        pass

class TextTranslation (BaseUITranslation):
    pass

class WebTranslation (BaseUITranslation):
    pass

__all__ = ['BaseUITranslation', 'TextTranslation', 'WebTranslation']
