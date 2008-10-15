import gtk
import gtkmozembed

import freespeak.utils as utils
import freespeak.ui.utils as uiutils
from freespeak.translation import *
from freespeak.status import *
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
        gtk.VBox.__init__ (self, spacing=12)
        BaseTranslation.__init__ (self, *args)

    def setup_label (self):
        self.label = TranslationLabel (self)
        self.label.show ()

    def setup_translation_box (self):
        self.translation_box = TranslationBox (self.application, self)
        self.translation_box.show ()

        self.translate_button = gtk.Button ("_Translate")
        self.translate_button.set_sensitive (False)
        self.translate_button.set_use_underline (True)
        image = gtk.image_new_from_stock (gtk.STOCK_REFRESH, gtk.ICON_SIZE_BUTTON)
        self.translate_button.set_image (image)
        self.translate_button.connect ('clicked', self.on_translate_clicked)
        self.translate_button.show ()

        self.translation_box.pack_start (self.translate_button, False)
        self.pack_start (self.translation_box, False)

    def setup_ui (self):
        pass

    def get_label (self):
        return self.label

    # Events

    def on_translate_clicked (self, button):
        request = self.create_request ()
        if request:
            self.translate (request)

    # Overrided methods

    def setup (self):
        self.setup_translation_box ()
        self.setup_label ()
        self.setup_ui ()

    def update_from_langs (self, langs):
        self.translation_box.update_from_langs (langs)

    def update_to_langs (self, langs):
        self.translation_box.update_to_langs (langs)

    @utils.syncronized
    def update_can_translate (self, can_translate):
        self.translate_button.set_sensitive (can_translate)

    # Virtual methods

    def create_request (self):
        raise NotImplementedError ()

class TextTranslation (BaseUITranslation):
    def setup_ui (self):
        self.source_buffer = gtk.TextBuffer ()
        view = gtk.TextView (self.source_buffer)
        view.show ()
        scrolled = uiutils.ScrolledWindow (view)
        scrolled.show ()
        frame = gtk.Frame (_("Text to translate"))
        frame.add (scrolled)
        frame.show ()
        self.pack_start (frame)

        self.dest_buffer = gtk.TextBuffer ()
        view = gtk.TextView (self.dest_buffer)
        view.set_editable (False)
        view.show ()
        scrolled = uiutils.ScrolledWindow (view)
        scrolled.show ()
        frame = gtk.Frame (_("Translated text"))
        frame.add (scrolled)
        frame.show ()
        self.pack_start (frame)

    def create_request (self):
        return TextTranslationRequest (self.source_buffer.get_text (self.source_buffer.get_start_iter (),
                                                                    self.source_buffer.get_end_iter ()))
    @utils.syncronized
    def update_status (self, status):
        if isinstance (status, StatusComplete):
            self.dest_buffer.set_text (status.result)

class WebTranslation (BaseUITranslation):
    def setup_ui (self):
        hbox = gtk.HBox (spacing=6)
        label = gtk.Label ("URL:")
        label.show ()
        hbox.pack_start (label, False)

        self.url = gtk.Entry ()
        self.url.set_sensitive (False)
        self.url.connect ('changed', self.on_url_changed)
        self.url.show ()
        hbox.pack_start (self.url)
        
        hbox.show ()
        self.pack_start (hbox, False)

        self.browser = gtkmozembed.MozEmbed ()
        self.browser.show ()
        self.pack_start (self.browser)

    def create_request (self):
        url = self.url.get_text ()
        if not url:
            uiutils.warning (_("Please insert an URL"))
        else:
            return WebTranslationRequest (self.url.get_text ())

    @utils.syncronized
    def update_can_translate (self, can_translate):
        self.url.set_sensitive (can_translate)
        self.translate_button.set_sensitive (can_translate and bool (self.url.get_text ()))

    @utils.syncronized
    def update_status (self, status):
        if isinstance (status, StatusComplete):
            self.browser.load_url (status.result)

    # Events

    def on_url_changed (self, entry):
        self.translate_button.set_sensitive (bool (entry.get_text ()))

__all__ = ['BaseUITranslation', 'TextTranslation', 'WebTranslation']
