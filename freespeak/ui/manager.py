import gtk

class Manager (gtk.Notebook):
    def __init__ (self, application):
        gtk.Notebook.__init__ (self)
        self.application = application

        gtk.rc_parse_string ("""
style "close-button-style"
{
  GtkWidget::focus-padding = 0
  xthickness = 0
  ythickness = 0
}
widget "*.close-button" style "close-button-style"
 """)

    def add_translation (self, translation):
        label = translation.get_label ()
        self.append_page (translation, label)
        translation.show ()

    def remove_translation (self, translation):
        page_num = self.page_num (translation)
        self.remove_page (page_num)

__all__ = ['Manager']
