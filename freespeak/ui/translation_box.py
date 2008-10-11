import gtk

class TranslationBox (gtk.HBox):
    def __init__ (self, application, translation):
        gtk.HBox.__init__ (self, 6)
        self.application = application
        self.translation = translation

__all__ = ['TranslationBox']


