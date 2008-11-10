import gtk
import gtkmozembed

import freespeak.utils as utils
import freespeak.ui.utils as uiutils
from freespeak.ui.spinner import Spinner
from freespeak.translation import *
from freespeak.status import *
from translation_box import *             

class TranslationLabel (gtk.HBox):
    def __init__ (self, application, translation):
        gtk.HBox.__init__ (self, spacing=2)
        self.application = application
        self.translation = translation

        self.title = 'Unnamed'
        self.is_custom = False

        self.setup_icon ()
        self.setup_label ()
        self.setup_entry ()
        self.setup_event_box ()
        self.setup_close ()
        self.be_label ()

        self.pack_start (self.icon)
        self.pack_start (self.event_box)
        self.pack_start (self.close, False, padding=4)

    def setup_icon (self):
        self.icon = Spinner (self.application, None)
        self.icon.show ()

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
        self.event_box.set_visible_window (False)
        self.event_box.connect ('button-press-event', self.on_event_box_button_press_event)
        self.event_box.connect ('key-press-event', self.on_event_box_key_press_event)
        self.event_box.show ()

    def setup_close (self):
        self.close = uiutils.TinyButton (gtk.STOCK_CLOSE)
        self.close.set_tooltip_text (_("Close this translation"))
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

    def start_loading (self):
        self.icon.start ()

    def stop_loading (self):
        self.icon.stop ()

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
        self.label = TranslationLabel (self.application, self)
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

    def setup_progress (self):
        self.progress = uiutils.Progress ()
        self.pack_start (self.progress, False)

    def setup_ui (self):
        pass

    def setup_clipboard (self):
        raise NotImplementedError ()

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
        self.setup_progress ()
        self.setup_clipboard ()

    def update_translator (self, translator):
        if translator:
            pixbuf = self.application.icon_theme.load_icon (translator.icon, Spinner.PIXELS, 0)
            self.label.icon.set_idle (pixbuf)

    def update_from_langs (self, langs):
        self.translation_box.update_from_langs (langs)

    def update_to_langs (self, langs):
        self.translation_box.update_to_langs (langs)

    @utils.syncronized
    def update_can_translate (self, can_translate):
        self.translate_button.set_sensitive (can_translate)

    @utils.syncronized
    def update_status (self, status):
        if isinstance (status, StatusStarted):
            self.progress.show ()
            self.progress.start ()
            self.label.start_loading ()
            self.set_sensitive (False)
        elif isinstance (status, StatusComplete):
            self.progress.hide ()
            self.progress.stop ()
            self.label.stop_loading ()
            self.set_sensitive (True)
        self.progress.set_text (status.description)

    # Virtual methods

    def create_request (self):
        raise NotImplementedError ()

class TextTranslation (BaseUITranslation):
    capability = TextTranslationRequest

    def translate_buttons (self):
        box = gtk.HBox (homogeneous=True)
        # Clear
        btn = uiutils.TinyButton (gtk.STOCK_CLEAR)
        btn.set_tooltip_text (_("Clear the text to translate"))
        btn.connect ('clicked', self.on_tiny_clear)
        btn.show ()
        box.pack_start (btn)
        # Paste
        btn = uiutils.TinyButton (gtk.STOCK_PASTE)
        btn.set_tooltip_text (_("Paste the text to translate from the clipboard"))
        btn.connect ('clicked', self.on_tiny_paste)
        btn.show ()
        box.pack_start (btn)
        box.show ()
        return box

    def translated_buttons (self):
        box = gtk.HBox (homogeneous=True)
        # Copy
        btn = self.tiny_copy = uiutils.TinyButton (gtk.STOCK_COPY)
        btn.set_tooltip_text (_("Copy translated text to the clipboard"))
        btn.connect ('clicked', self.on_tiny_copy)
        btn.set_sensitive (False)
        btn.show ()
        box.pack_start (btn)
        # Swap
        btn = self.tiny_swap = uiutils.TinyButton (gtk.STOCK_CONVERT)
        btn.set_tooltip_text (_("Swap both the source text with the translated text and the languages"))
        btn.connect ('clicked', self.on_tiny_swap)
        btn.set_sensitive (False)
        btn.show ()
        box.pack_start (btn)

        box.show ()
        return box

    def setup_ui (self):
        self.source_buffer = gtk.TextBuffer ()
        view = self.source_view = gtk.TextView (self.source_buffer)
        view.show ()
        scrolled = uiutils.ScrolledWindow (view)
        scrolled.show ()
        frame = uiutils.Frame (_("Text to translate"), self.translate_buttons ())
        frame.add (scrolled)
        frame.show ()
        self.pack_start (frame)

        self.dest_buffer = gtk.TextBuffer ()
        view = gtk.TextView (self.dest_buffer)
        view.set_editable (False)
        view.modify_base (gtk.STATE_NORMAL, gtk.gdk.color_parse ("#fff8ae"))
        view.show ()
        scrolled = uiutils.ScrolledWindow (view)
        scrolled.show ()
        frame = uiutils.Frame (_("Translated text"), self.translated_buttons ())
        frame.add (scrolled)
        frame.show ()
        self.pack_start (frame)

    def get_source_contents (self):
        return self.source_buffer.get_text (self.source_buffer.get_start_iter (),
                                            self.source_buffer.get_end_iter ())

    def get_dest_contents (self):
        return self.dest_buffer.get_text (self.dest_buffer.get_start_iter (),
                                          self.dest_buffer.get_end_iter ())

    def setup_clipboard (self):
        contents = self.application.clipboard.get_contents ()
        # Also check it's not an URL
        if contents is not None and not (contents.startswith ("http") and not ' ' in contents.strip()):
            self.source_buffer.set_text (contents)

    def create_request (self):
        return TextTranslationRequest (self.get_source_contents ())

    def update_dest_actions (self):
        has_text = bool (self.get_dest_contents ())
        has_to_lang = bool (self.translation_box.to_combo.get_active_iter ())
        self.tiny_swap.set_sensitive (has_to_lang and has_text)
        self.tiny_copy.set_sensitive (has_text)

    @utils.syncronized
    def update_status (self, status):
        BaseUITranslation.update_status (self, status)
        if isinstance (status, StatusTextComplete):
            self.dest_buffer.set_text (status.result)
            self.application.clipboard.set_contents (status.result)
            self.update_dest_actions ()

    @utils.syncronized
    def update_can_translate (self, can_translate):
        BaseUITranslation.update_can_translate (self, can_translate)
        self.update_dest_actions ()

    # Events
    def on_tiny_clear (self, button):
        self.source_buffer.set_text ("")
        self.source_view.grab_focus ()

    def on_tiny_paste (self, button):
        contents = self.application.clipboard.get_contents (force=True)
        if contents is not None:
            self.source_buffer.set_text (contents)

    def on_tiny_copy (self, button):
        self.application.clipboard.set_contents (self.get_dest_contents (), force=True)

    def on_tiny_swap (self, button):
        source_contents = self.get_source_contents ()
        self.source_buffer.set_text (self.get_dest_contents ())
        self.dest_buffer.set_text (source_contents)
        self.translation_box.swap_langs ()

class WebTranslation (BaseUITranslation):
    capability = WebTranslationRequest

    def url_buttons (self):
        box = gtk.HBox (homogeneous=True)
        # Clear
        btn = uiutils.TinyButton (gtk.STOCK_CLEAR)
        btn.set_tooltip_text (_("Clear the url"))
        btn.connect ('clicked', self.on_tiny_clear)
        btn.show ()
        box.pack_start (btn)
        # Paste
        btn = uiutils.TinyButton (gtk.STOCK_PASTE)
        btn.set_tooltip_text (_("Paste the url from the clipboard"))
        btn.connect ('clicked', self.on_tiny_paste)
        btn.show ()
        box.pack_start (btn)
        box.show ()
        return box

    def setup_ui (self):
        hbox = self.url_box = gtk.HBox (spacing=6)
        label = gtk.Label ("URL:")
        label.show ()
        hbox.pack_start (label, False)

        self.url = gtk.Entry ()
        self.url.connect ('changed', self.on_url_changed)
        self.url.show ()
        hbox.pack_start (self.url)
        
        hbox.pack_start (self.url_buttons (), False)

        hbox.set_sensitive (False)
        hbox.show ()
        self.pack_start (hbox, False)

        self.browser = gtkmozembed.MozEmbed ()
        self.browser.show ()
        self.pack_start (self.browser)

    def setup_clipboard (self):
        contents = self.application.clipboard.get_contents ()
        if contents is not None and contents.startswith("http"):
            self.url.set_text (contents)

    def create_request (self):
        url = self.url.get_text ()
        if not url:
            uiutils.warning (_("Please insert an URL"))
        else:
            return WebTranslationRequest (self.url.get_text ())

    @utils.syncronized
    def update_can_translate (self, can_translate):
        self.url_box.set_sensitive (can_translate)
        self.translate_button.set_sensitive (can_translate and bool (self.url.get_text ()))

    @utils.syncronized
    def update_status (self, status):
        BaseUITranslation.update_status (self, status)
        if isinstance (status, StatusWebComplete):
            self.browser.load_url (status.result)
            self.application.clipboard.set_contents (status.result)

    # Events

    def on_url_changed (self, entry):
        self.translate_button.set_sensitive (bool (entry.get_text ()))

    def on_tiny_clear (self, button):
        self.url.set_text ("")
        self.url.grab_focus ()

    def on_tiny_paste (self, button):
        contents = self.application.clipboard.get_contents (force=True)
        if contents is not None:
            self.url.set_text (contents)

__all__ = ['BaseUITranslation', 'TextTranslation', 'WebTranslation']
