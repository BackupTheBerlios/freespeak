import gtk

from freespeak.ui.translation import BaseUITranslation
import freespeak.ui.utils as uiutils

class TranslationSuggestions (BaseUITranslation):
    def setup_ui (self):
        hbox = gtk.HBox (spacing=6)
        label = gtk.Label ("Suggest")
        label.show ()
        hbox.pack_start (label, False)

        self.entry = gtk.Entry ()
        self.entry.show ()
        hbox.pack_start (self.entry)
        
        hbox.show ()
        self.pack_start (hbox, False)

        self.suggestions = gtk.VBox (spacing=6)
        self.suggestions.show ()
        viewport = gtk.Viewport ()
        viewport.add (self.suggestions)
        viewport.modify_bg (gtk.STATE_NORMAL, self.DESTINATION_COLOR)
        viewport.show ()
        scrolled = uiutils.ScrolledWindow (viewport)
        scrolled.set_shadow_type (gtk.SHADOW_NONE)
        scrolled.show ()
        self.pack_start (scrolled)

    def setup_clipboard (self):
        contents = self.application.clipboard.get_contents ()
        if contents is not None:
            self.entry.set_text (contents)

    def create_request (self):
        return TranslationSuggestionsRequest (self.entry.get_text ())
