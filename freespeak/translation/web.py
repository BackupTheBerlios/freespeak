from base import BaseTranslation
import gtk, gtk.gdk
from src.utils import *
from src.progress import Progress

class WebTranslation(gtk.VBox, BaseTranslation):
    def __init__(self, parent, preferred):
        gtk.VBox.__init__(self)
        self._parent = parent
        self.tabbed = True
        self.set_spacing(6)

        hbox = gtk.HBox(spacing=8)
        mhbox = gtk.HBox(spacing=4)
        mhbox.pack_start(make_label(_('T<u>r</u>anslator:')), 0, 0)
        self.w_module = self._parent._parent.make_combo_modules("web")
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

        hbox = gtk.HBox(spacing=12)
        hbox.pack_start(make_label(_("Web Page <u>U</u>RL:")), 0, 0)
        self.w_source = gtk.Entry()
        hbox.pack_start(self.w_source)
        self.w_source.add_accelerator("grab-focus",
                                      self._parent._parent.accel_group,
                                      accel_key(_("Web Page <u>U</u>RL:")),
                                      gtk.gdk.MOD1_MASK, gtk.ACCEL_VISIBLE)

        self.w_browser = make_button(_("<u>V</u>iew in browser"),
                                     gtk.STOCK_REDO)
        self.w_browser.set_sensitive(0)
        hbox.pack_start(self.w_browser,0 ,0)
        self.pack_start(hbox, 0, 0)

        try:
            import gtkhtml2
            self.document = gtkhtml2.Document()
            self.document.clear()
            self.document.open_stream("text/html")
            self.document.write_stream("<html></html>")
            self.document.close_stream()

            self.w_result = gtkhtml2.View()
            self.w_result.set_document(self.document)
        except:
            self.w_result = gtk.TextView()
            self.w_result.set_sensitive(0)

        self.pack_start(make_text(self.w_result))
        
        self.progress = Progress()
        self.pack_start(self.progress, expand=False)

        self.w_module.connect("changed", self.on_module)
        self.w_module.add_accelerator("grab-focus",
                                      self._parent._parent.accel_group,
                                      accel_key(_("T<u>r</u>anslator:")),
                                      gtk.gdk.MOD1_MASK, gtk.ACCEL_VISIBLE)

        self.w_from.connect("changed", self.on_from)
        self.w_from.add_accelerator("grab-focus",
                                    self._parent._parent.accel_group,
                                    accel_key(_("<u>F</u>rom:")),
                                    gtk.gdk.MOD1_MASK, gtk.ACCEL_VISIBLE)

        self.w_to.connect("changed", self.on_to)
        self.w_to.add_accelerator("grab-focus",
                                  self._parent._parent.accel_group,
                                  accel_key(_("T<u>o</u>:")),
                                  gtk.gdk.MOD1_MASK, gtk.ACCEL_VISIBLE)
        if preferred:
            self._parent._parent.preferred_combo_module(self.w_module)

    def on_browser(self, w, data):
        print browser

    def get_source(self):
        return self.w_source.get_text()

    def set_result(self, result, browser=False):
        if browser:
            try:
                import gnome.ui
                gnome.ui.url_show_on_screen(result[1],
                                            self._parent._parent.get_screen())
            except:
                pass
            return
        try:
            self.document.clear()
            self.document.open_stream('text/html')
            self.document.write_stream(result[0])
            self.document.close_stream()
        except:
            print "browser"
