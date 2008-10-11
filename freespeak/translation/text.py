from base import BaseTranslation
import gtk, gtk.gdk
from src.utils import *
from src.progress import Progress

class TextTranslation(gtk.VBox, BaseTranslation):
    def __init__(self, parent, preferred):
        gtk.VBox.__init__(self)
        self._parent = parent
        self.tabbed = True
        self.set_spacing(6)

        hbox = gtk.HBox(spacing=8)
        mhbox = gtk.HBox(spacing=4)
        mhbox.pack_start(make_label(_('T<u>r</u>anslator:')), 0, 0)
        self.w_module = self._parent._parent.make_combo_modules()
        mhbox.pack_start(self.w_module)
        hbox.pack_start(mhbox)

        mhbox = gtk.HBox(spacing=4)
        mhbox.pack_start(make_label(_("<u>F</u>rom:")), 0, 0)
        self.w_from = Combo()
        self.w_from.set_sensitive(0)
        mhbox.pack_start(self.w_from)
        hbox.pack_start(mhbox) 

        mhbox = gtk.HBox(spacing=4)
        mhbox.pack_start(make_label(_('T<u>o</u>:')), 0, 0)
        self.w_to = Combo()
        self.w_to.set_sensitive(0)
        mhbox.pack_start(self.w_to)
        hbox.pack_start(mhbox)

        self.w_translate = make_button(_('<u>T</u>ranslate!'),
                                       gtk.STOCK_REFRESH)
        self.w_translate.set_sensitive(0)
        hbox.pack_start(self.w_translate, 0, 0)
        self.pack_start(hbox, 0, 0)

        buffer = gtk.TextBuffer() 
        if (self._parent._parent.config.getboolean('clipboard', 'get') and
            self._parent._parent.clipboard.wait_is_text_available()):
            text = self._parent._parent.clipboard.wait_for_text()
            if text != self._parent.cur_clipboard:
                buffer.paste_clipboard(self._parent._parent.clipboard, None, 1)
                self._parent._parent.cur_clipboard = text
                self._parent._parent.clipboard.clear()
        self.w_source = gtk.TextView(buffer)
        self.w_source.set_wrap_mode(gtk.WRAP_WORD)
        self.pack_start(make_text(self.w_source))
        self.pack_start(gtk.HSeparator(), 0, 0)
        self.w_textto = gtk.TextView()
        self.w_textto.set_wrap_mode(gtk.WRAP_WORD)
        self.pack_start(make_text(self.w_textto))
        self.progress = Progress()
        self.pack_start(self.progress, expand=False)

        self.w_module.connect("changed", self.on_module)
        self.w_module.add_accelerator("grab-focus", parent.accel_group,
                                      accel_key(_("T<u>r</u>anslator:")),
                                      gtk.gdk.MOD1_MASK, gtk.ACCEL_VISIBLE)

        self.w_from.connect("changed", self.on_from)
        self.w_from.add_accelerator("grab-focus", parent.accel_group,
                                    accel_key(_("<u>F</u>rom:")),
                                    gtk.gdk.MOD1_MASK, gtk.ACCEL_VISIBLE)

        self.w_to.connect("changed", self.on_to)
        self.w_to.add_accelerator("grab-focus", parent.accel_group,
                                  accel_key(_("T<u>o</u>:")),
                                  gtk.gdk.MOD1_MASK, gtk.ACCEL_VISIBLE)
        if preferred:
            self._parent._parent.preferred_combo_module(self.w_module)

    def get_source(self):
        buffer = self.w_source.get_buffer()
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter())
        return text

    def set_result(self, text, browser=False):
        buffer = gtk.TextBuffer()
        buffer.set_text(text)
        self.w_textto.set_buffer(buffer)
        if self._parent._parent.config.getboolean('clipboard', 'set'):
            self._parent._parent.clipboard.set_text(text)
            self._parent._parent.cur_clipboard = text
