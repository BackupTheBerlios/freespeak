import gtk

class Manager (gtk.Notebook):
    def __init__ (self, application):
        gtk.Notebook.__init__ (self)
        self.application = application

    def add_translation (self, translation):
        label = translation.get_label ()
        self.append_page (translation, label)
        translation.show ()

    def remove_translation (self, translation):
        page_num = self.page_num (translation)
        self.remove_page (page_num)

__all__ = ['Manager']
