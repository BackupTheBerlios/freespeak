import gtk

from freespeak.translation import *
from translation_box import *

class BaseUITranslation (gtk.VBox, BaseTranslation):
    def __init__ (self, *args):
        gtk.VBox.__init__ (self, spacing=6)
        BaseTranslation.__init__ (self, *args)

    def setup (self):
        self.setup_translation_box ()
        self.setup_ui ()

    def setup_translation_box (self):
        self.translation_box = TranslationBox (self.application, self)
        self.translation_box.show ()

    def setup_ui (self):
        pass

class TextTranslation (BaseUITranslation):
    def setup_ui (self):
        self.pack_start (self.translation_box, False)
        label = gtk.Label ("Translation")
        label.show ()
        self.pack_start (label)

class WebTranslation (BaseUITranslation):
    pass

__all__ = ['BaseUITranslation', 'TextTranslation', 'WebTranslation']
