# FreeSpeak - a GUI frontend to online translator engines
# freespeak/ui/translation.py
#
## Copyright (C) 2005, 2006, 2007, 2008, 2009  Luca Bruno <lethalman88@gmail.com>
##
## This file is part of FreeSpeak.
##   
## FreeSpeak is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##    
## FreeSpeak is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Library General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA.

"""
Classes for building translation pages
"""

import gtk
import gtkmozembed
import gtkspell
import gnome

import freespeak.utils as utils
import freespeak.ui.utils as uiutils
from freespeak.translation import (BaseTranslation,
                                   TextTranslationRequest,
                                   WebTranslationRequest)
from freespeak.status import (StatusStarted, StatusCancelled, StatusComplete,
                              StatusTextComplete, StatusWebComplete)
from freespeak.ui.spinner import Spinner
from freespeak.ui.translation_label import TranslationLabel
from freespeak.ui.translation_box import TranslationBox

class BaseUITranslation (gtk.VBox, BaseTranslation):
    """
    The basic translation page class
    """
    capability = None
    DESTINATION_COLOR = gtk.gdk.color_parse ("#fff8ae")

    def __init__ (self, *args):
        gtk.VBox.__init__ (self, spacing=12)
        BaseTranslation.__init__ (self, *args)

    def setup_layout (self):
        """
        Setup the layout of the container
        """
        self.layout = gtk.VBox (spacing=12)
        self.layout.show ()
        self.pack_start (self.layout)

    def setup_label (self):
        """
        Create the tab label for the notebook
        """
        self.label = TranslationLabel (self.application, self)
        self.label.show ()

    def setup_translation_box (self):
        """
        Pack the translation box
        """
        self.translation_box = TranslationBox (self.application, self)
        self.translation_box.show ()

        self.translate_button = gtk.Button ("_Translate")
        self.translate_button.set_sensitive (False)
        self.translate_button.set_use_underline (True)
        image = gtk.image_new_from_stock (gtk.STOCK_REFRESH,
                                          gtk.ICON_SIZE_BUTTON)
        self.translate_button.set_image (image)
        self.translate_button.connect ('clicked', self.on_translate_clicked)
        self.translate_button.show ()

        self.translation_box.pack_start (self.translate_button, False)
        self.layout.pack_start (self.translation_box, False)

    def setup_progress (self):
        """
        Create the progress bar
        """
        self.progress = uiutils.Progress ()
        self.progress.connect ('cancelled', self.on_cancelled)
        self.pack_start (self.progress, False)

    def setup_ui (self):
        """
        Virtual method, should be implemented in subclasses to add
        custom widgets.
        """
        pass

    def setup_clipboard (self):
        """
        Virtual method, must be implemented.
        Will handle the clipboard when the translation is begin opened.
        """
        raise NotImplementedError ()

    def get_label (self):
        """
        Returns the tab label for the manager
        """
        return self.label

    def started (self):
        """
        Internally called to indicate the translation has been started
        """
        self.progress.show ()
        self.progress.start ()
        self.label.start_loading ()
        self.layout.set_sensitive (False)

    def stopped (self):
        """
        Internally called to indicate the translation has been stopped
        """
        self.progress.hide ()
        self.progress.stop ()
        self.label.stop_loading ()
        self.layout.set_sensitive (True)

    # Events

    def on_translate_clicked (self, button):
        """
        Start the real translation when the Translate button is clicked
        """
        request = self.create_request ()
        if request:
            self.translate (request)

    def on_cancelled (self, progress):
        """
        Cancellation button has been called.
        This will request the cancellation of the translation.
        """
        self.cancel ()

    # Overrided methods

    def setup (self):
        """
        Setup the whole widget
        """
        self.setup_layout ()
        self.setup_translation_box ()
        self.setup_label ()
        self.setup_ui ()
        self.setup_progress ()
        self.setup_clipboard ()

    @utils.syncronized
    def update_translator (self, translator):
        """
        Update the translator. This will dispatch the event to the
        translation box and set the translation icon in the tab label.
        """
        self.translation_box.set_translator (translator)
        if translator:
            pixbuf = self.application.icon_theme.load_icon (translator.icon,
                                                            Spinner.PIXELS, 0)
            self.label.icon.set_idle (pixbuf)

    def update_from_lang (self, lang):
        """
        Externally called to change the source language
        """
        self.translation_box.set_from_lang (lang)

    def update_to_lang (self, lang):
        """
        Externally called to change the destination language
        """
        self.translation_box.set_to_lang (lang)

    def update_from_langs (self, langs):
        """
        Externally called to change the list of source languages
        """
        self.translation_box.update_from_langs (langs)

    def update_to_langs (self, langs):
        """
        Externally called to change the list of destination languages
        """
        self.translation_box.update_to_langs (langs)

    @utils.syncronized
    def update_can_translate (self, can_translate):
        """
        Externally called to notify whether we can start the translation
        """
        self.translate_button.set_sensitive (can_translate)

    @utils.syncronized
    def update_status (self, status):
        """
        Externally called whenever the status of the translation changes
        """
        if isinstance (status, StatusStarted):
            self.started ()
        elif (isinstance (status, StatusComplete)
              or isinstance (status, StatusCancelled)):
            self.stopped ()
        self.progress.set_text (status.description)

    # Virtual methods

    def create_request (self):
        """
        Virtual method, must be implemented to create the translation request
        """
        raise NotImplementedError ()


class TextTranslation (BaseUITranslation):
    """
    Text translation container
    """
    capability = TextTranslationRequest

    def translate_buttons (self):
        """
        Tiny buttons for the source text
        """
        box = gtk.HBox (homogeneous=True)
        # Clear
        btn = uiutils.TinyButton (gtk.STOCK_CLEAR)
        btn.set_tooltip_text (_("Clear the text to translate"))
        btn.connect ('clicked', self.on_tiny_clear)
        btn.show ()
        box.pack_start (btn)
        # Paste
        btn = uiutils.TinyButton (gtk.STOCK_PASTE)
        tooltip_text = _("Paste the text to translate from the clipboard")
        btn.set_tooltip_text (tooltip_text)
        btn.connect ('clicked', self.on_tiny_paste)
        btn.show ()
        box.pack_start (btn)
        box.show ()
        return box

    def translated_buttons (self):
        """
        Tiny buttons for the destination text
        """
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
        """
        Setup the text views
        """
        self.source_buffer = gtk.TextBuffer ()
        view = self.source_view = gtk.TextView (self.source_buffer)
        view.show ()
        gtkspell.Spell (view)
        scrolled = uiutils.ScrolledWindow (view)
        scrolled.show ()
        frame = uiutils.Frame (_("Text to translate"),
                               self.translate_buttons ())
        frame.add (scrolled)
        frame.show ()
        self.layout.pack_start (frame)

        self.dest_buffer = gtk.TextBuffer ()
        view = gtk.TextView (self.dest_buffer)
        view.set_editable (False)
        view.modify_base (gtk.STATE_NORMAL, self.DESTINATION_COLOR)
        view.show ()
        scrolled = uiutils.ScrolledWindow (view)
        scrolled.show ()
        frame = uiutils.Frame (_("Translated text"), self.translated_buttons ())
        frame.add (scrolled)
        frame.show ()
        self.layout.pack_start (frame)

    def get_source_contents (self):
        """
        Util to get the contents of the text to be translated
        """
        return self.source_buffer.get_text (self.source_buffer.get_start_iter(),
                                            self.source_buffer.get_end_iter ())

    def get_dest_contents (self):
        """
        Util to get the contents of the translated text
        """
        return self.dest_buffer.get_text (self.dest_buffer.get_start_iter (),
                                          self.dest_buffer.get_end_iter ())

    def setup_clipboard (self):
        """
        Get the text contents from the clipboard
        """
        contents = self.application.clipboard.get_text_contents ()
        if contents is not None:
            self.source_buffer.set_text (contents)

    def create_request (self):
        """
        Create a text translation request
        """
        return TextTranslationRequest (self.get_source_contents ())

    def update_dest_actions (self):
        """
        Update dest tiny buttons sensitivity
        """
        has_text = bool (self.get_dest_contents ())
        has_to_lang = bool (self.translation_box.to_combo.get_active_iter ())
        self.tiny_swap.set_sensitive (has_to_lang and has_text)
        self.tiny_copy.set_sensitive (has_text)

    @utils.syncronized
    def update_status (self, status):
        """
        Update destionation widgets when the text translation is complete
        """
        BaseUITranslation.update_status (self, status)
        if isinstance (status, StatusTextComplete):
            self.dest_buffer.set_text (status.result)
            self.application.clipboard.set_contents (status.result)
            self.update_dest_actions ()

    @utils.syncronized
    def update_can_translate (self, can_translate):
        """
        Both chain up to the parent class and update destination actions
        """
        BaseUITranslation.update_can_translate (self, can_translate)
        self.update_dest_actions ()

    # Events
    def on_tiny_clear (self, button):
        """
        Clear the source buffer
        """
        self.source_buffer.set_text ("")
        self.source_view.grab_focus ()

    def on_tiny_paste (self, button):
        """
        Paste the clipboard contents to the source buffer
        """
        contents = self.application.clipboard.get_contents ()
        if contents is not None:
            self.source_buffer.set_text (contents)

    def on_tiny_copy (self, button):
        """
        Copy the translated text to the clipboard
        """
        self.application.clipboard.set_contents (self.get_dest_contents (),
                                                 force=True)

    def on_tiny_swap (self, button):
        """
        Swap both the text buffers and the languages in the translation box
        """
        source_contents = self.get_source_contents ()
        self.source_buffer.set_text (self.get_dest_contents ())
        self.dest_buffer.set_text (source_contents)
        self.translation_box.swap_langs ()

class WebTranslation (BaseUITranslation):
    """
    Web page translation
    """
    capability = WebTranslationRequest

    def source_url_buttons (self):
        """
        Tiny buttons for the source url entry
        """
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

    def dest_url_buttons (self):
        """
        Tiny buttons for the destination url
        """
        box = gtk.HBox (homogeneous=True)
        # Copy
        btn = uiutils.TinyButton (gtk.STOCK_COPY)
        btn.set_tooltip_text (_("Copy the translated page url"))
        btn.connect ('clicked', self.on_tiny_copy)
        btn.show ()
        box.pack_start (btn)

        box.show ()
        return box

    def setup_ui (self):
        """
        Hold a source box, a mozilla browser and a destination box
        """
        self.can_translate = False

        # Source box
        hbox = gtk.HBox (spacing=6)
        label = gtk.Label ("URL:")
        label.show ()
        hbox.pack_start (label, False)

        self.source_url = gtk.Entry ()
        self.source_url.connect ('changed', self.on_source_url_changed)
        self.entry_activate_handler = self.source_url.connect ('activate', lambda *args: self.translate_button.clicked ())
        self.source_url.handler_block (self.entry_activate_handler)
        self.source_url.show ()
        hbox.pack_start (self.source_url)
        
        hbox.pack_start (self.source_url_buttons (), False)

        hbox.show ()
        self.layout.pack_start (hbox, False)

        # Browser
        self.browser = gtkmozembed.MozEmbed ()
        self.browser.connect ('net-stop', self.on_browser_net_stop)
        self.browser.show ()
        self.layout.pack_start (self.browser)

        # Destination box
        self.dest_url_box = gtk.EventBox ()
        self.dest_url_box.set_visible_window (False)
        self.dest_url_box.modify_bg (gtk.STATE_NORMAL, self.DESTINATION_COLOR)
        self.dest_url_box.set_sensitive (False)
        hbox = gtk.HBox (spacing=6)
        self.dest_url_box.add (hbox)

        self.dest_url = gtk.LinkButton ("", "Translated URL")
        self.dest_url.show ()
        gtk.link_button_set_uri_hook (self.dest_url_hook)
        hbox.pack_start (self.dest_url)
        
        hbox.pack_start (self.dest_url_buttons (), False)

        hbox.show ()
        self.layout.pack_start (self.dest_url_box, False)

    def setup_clipboard (self):
        """
        Take url contents from the clipboard to the url entry
        """
        contents = self.application.clipboard.get_url_contents ()
        if contents is not None:
            self.source_url.set_text (contents)

    def create_request (self):
        """
        Create a web translation request
        """
        url = self.source_url.get_text ()
        if not url:
            uiutils.warning (_("Please insert an URL"))
        else:
            return WebTranslationRequest (self.source_url.get_text ())

    @utils.syncronized
    def update_can_translate (self, can_translate):
        """
        Take in consideration the entry contents when updating the translate
        button sensitivity
        """
        self.can_translate = can_translate
        self.update_translate_button_sensitivity ()

    def update_translate_button_sensitivity (self):
        """
        Translate button sensitivity depends on the entry contents
        """
        sensitivity = self.can_translate and bool (self.source_url.get_text ())
        self.translate_button.set_sensitive (sensitivity)
        if sensitivity:
            self.source_url.handler_unblock (self.entry_activate_handler)
        else:
            self.source_url.handler_block (self.entry_activate_handler)

    @utils.syncronized
    def update_status (self, status):
        """
        Take in consideration the status of the browser as it runs asyncronously
        """
        if isinstance (status, StatusWebComplete):
            self.dest_url.set_uri (status.result)
            self.browser.load_url (status.result)
            self.application.clipboard.set_contents (status.result)
            self.progress.set_text (_("Fetching page..."))
            return

        if isinstance (status, StatusCancelled):
            self.browser.stop_load ()
        
        BaseUITranslation.update_status (self, status)

    # Events

    def on_source_url_changed (self, entry):
        """
        Change the translate button sensitivity whenever the entry
        contents change
        """
        self.update_translate_button_sensitivity ()

    def dest_url_hook (self, button, uri):
        """
        Open the translated page in a browser
        """
        gnome.url_show (uri)

    def on_tiny_clear (self, button):
        """
        Clear the source url entry
        """
        self.source_url.set_text ("")
        self.source_url.grab_focus ()

    def on_tiny_paste (self, button):
        """
        Paste che clipboard contents to the url entry
        """
        contents = self.application.clipboard.get_contents ()
        if contents is not None:
            self.source_url.set_text (contents)

    def on_tiny_copy (self, button):
        """
        Copy the url of the translated page into the clipboard
        """
        self.application.clipboard.set_contents (self.dest_url.get_uri (),
                                                 force=True)

    def on_browser_net_stop (self, browser):
        """
        Check whether the browser finished loading the page then
        update the translation widget
        """
        if self.progress.is_running ():
            self.dest_url_box.set_sensitive (True)
            self.dest_url_box.show ()
            self.dest_url_box.set_visible_window (True)
            self.stopped ()

__all__ = ['BaseUITranslation', 'TextTranslation', 'WebTranslation']
