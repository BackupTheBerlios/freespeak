import gtk

from freespeak.translation import *
from translation_box import *

class TranslationLabel (gtk.HBox):
    def __init__ (self, translation):
        gtk.HBox.__init__ (self, spacing=6)
        self.translation = translation

        self.title = 'Unnamed'
        self.is_custom = False

        self.setup_label ()
        self.setup_entry ()
        self.setup_event_box ()
        self.setup_close ()
        self.be_label ()

        self.pack_start (self.event_box)
        self.pack_start (self.close, False)

    def setup_label (self):
        self.label = gtk.Label ()
        self.label.show ()

    def setup_entry (self):
        self.entry = gtk.Entry ()
        self.entry_focus_out = self.entry.connect ('focus-out-event', self.on_entry_activate)
        self.entry.connect ('activate', self.on_entry_activate)
        self.entry.show ()

    def setup_event_box (self):
        self.event_box = gtk.EventBox ()
        self.event_box.connect ('button-press-event', self.on_event_box_button_press_event)
        self.event_box.connect ('key-press-event', self.on_event_box_key_press_event)
        self.event_box.show ()

    def setup_close (self):
        self.close = gtk.Button ()
        image = gtk.image_new_from_stock (gtk.STOCK_CLOSE, gtk.ICON_SIZE_BUTTON)
        self.close.set_image (image)
        self.close.connect ('clicked', self.on_close)
        self.close.show ()

    def drop_child (self):
        child = self.event_box.get_child ()
        if child:
            self.event_box.remove (child)

    def be_label (self):
        self.drop_child ()
        self.label.set_text (self.title)
        self.event_box.add (self.label)

    def be_entry (self):
        self.drop_child ()
        self.entry.set_text (self.title)
        self.event_box.add (self.entry)

    def set_suggested_title (self, title):
        if not self.is_custom:
            self.title = title
            self.label.set_text (title)

    # Events

    def on_event_box_button_press_event (self, event_box, event):
        if event.type == gtk.gdk._2BUTTON_PRESS:
            self.be_entry ()
            self.entry.grab_focus ()

    def on_event_box_key_press_event (self, event_box, event):
        # ESC key
        if event.keyval == 65307:
            self.entry.handler_block (self.entry_focus_out)
            self.be_label ()
            self.entry.handler_unblock (self.entry_focus_out)

    def on_entry_activate (self, entry, *args):
        self.title = entry.get_text ()
        self.entry.handler_block (self.entry_focus_out)
        self.be_label ()
        self.entry.handler_unblock (self.entry_focus_out)

        self.is_custom = True

    def on_close (self, button):
        self.translation.close ()

class BaseUITranslation (gtk.VBox, BaseTranslation):
    def __init__ (self, *args):
        gtk.VBox.__init__ (self, spacing=6)
        BaseTranslation.__init__ (self, *args)

    def setup (self):
        self.setup_translation_box ()
        self.setup_label ()
        self.setup_ui ()

    def setup_label (self):
        self.label = TranslationLabel (self)
        self.label.show ()

    def setup_translation_box (self):
        self.translation_box = TranslationBox (self.application, self)
        self.translation_box.show ()

    def setup_ui (self):
        pass

    def get_label (self):
        return self.label

class TextTranslation (BaseUITranslation):
    def setup_ui (self):
        self.pack_start (self.translation_box, False)
        label = gtk.Label ("Translation")
        label.show ()
        self.pack_start (label)

class WebTranslation (BaseUITranslation):
    pass

__all__ = ['BaseUITranslation', 'TextTranslation', 'WebTranslation']
