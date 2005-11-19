from base import BaseTranslation
import gtk, gtk.gdk
import thread
from src.utils import *

class MiniTranslation(gtk.Window, BaseTranslation):
    class Popup(gtk.Dialog):
        def __init__(self, parent, text, translated):
            gtk.Dialog.__init__(self, 'FreeSpeak - '+_('Translation'), parent,
                                0, (gtk.STOCK_CLOSE, gtk.RESPONSE_OK))
            self.set_position(gtk.WIN_POS_CENTER)
            self.set_border_width(4)
            self.set_resizable(1)
            self.vbox.set_spacing(6)

            label = gtk.Label()
            label.set_markup(_('From')+
                    ' <b>'+parent.w_from.get_active_text()+'</b> '+
                    _('to')+
                    ' <b>'+parent.w_to.get_active_text()+'</b> '+
                    _('using')+
                    ' <b>'+parent.w_module.get_active_text()+'</b>')
            label.show()
            self.vbox.pack_start(label, 0, 0)
            
            w_text = gtk.TextView()
            w_text.set_wrap_mode(gtk.WRAP_WORD)
            w_text.get_buffer().set_text(text)
            w_text.set_sensitive(0)
            scroll = make_text(w_text)
            scroll.show()
            self.vbox.pack_start(scroll)
            
            w_text = gtk.TextView()
            w_text.set_wrap_mode(gtk.WRAP_WORD)
            w_text.get_buffer().set_text(translated)
            w_text.set_sensitive(0)
            scroll = make_text(w_text)
            scroll.show()
            self.vbox.pack_start(scroll)
            
    def __init__(self, parent):
        gtk.Window.__init__(self)
        self.tabbed = False
        self.set_title('FreeSpeak')
        
        self.connect('show', self.on_show)
        self._parent = parent
        self.translating = 0
        self.set_keep_above(1)
        self.set_icon(self._parent.get_icon())

        self.update_trayicon_settings()

        hbox = gtk.HBox(spacing=3)
        
        self.w_normalize = make_button('', gtk.STOCK_CONVERT)
        self.w_normalize.connect('clicked', self.on_normalize)
        self.t_normalize = gtk.Tooltips()
        self.t_normalize.set_tip(self.w_normalize, _("Restore normal window"))
        self.t_normalize.enable()
        hbox.pack_start(self.w_normalize, 0, 0)
        self.w_module = self._parent.make_combo_modules()
        hbox.pack_start(self.w_module)
        
        self.w_from = Combo()
        self.w_from.set_sensitive(0)
        hbox.pack_start(self.w_from)
        
        self.w_to = Combo()
        self.w_to.set_sensitive(0)
        hbox.pack_start(self.w_to)
     
        self.w_translate = make_button('', gtk.STOCK_REFRESH)
        self.w_translate.set_sensitive(0)
        self.t_translate = gtk.Tooltips()
        self.t_translate.set_tip(self.w_translate,
                                 _("Translate clipboard text"))
        self.t_translate.enable()

        hbox.pack_start(self.w_translate, 0, 0)
        
        self.w_module.connect("changed", self.on_module)
        self.w_from.connect("changed", self.on_from)
        self.w_to.connect("changed", self.on_to)
        self.w_translate.connect("clicked", self.on_translate)

        accel_group = gtk.AccelGroup()
        self.w_module.add_accelerator("grab-focus", accel_group,
                                      accel_key(_("T<u>r</u>anslator:")),
                                      gtk.gdk.MOD1_MASK, gtk.ACCEL_VISIBLE)
        self.w_from.add_accelerator("grab-focus", accel_group,
                                    accel_key(_("<u>F</u>rom:")),
                                    gtk.gdk.MOD1_MASK, gtk.ACCEL_VISIBLE)

        self.w_to.add_accelerator("grab-focus", accel_group,
                                  accel_key(_("T<u>o</u>:")),
                                  gtk.gdk.MOD1_MASK, gtk.ACCEL_VISIBLE)
        self.w_translate.add_accelerator('clicked', accel_group, ord('T'),
                                         gtk.gdk.CONTROL_MASK, 0)
        self.w_normalize.add_accelerator('clicked', accel_group, ord('r'),
                                         gtk.gdk.CONTROL_MASK, 0)
        self.add_accel_group(accel_group)
        
        self.add(hbox)
        

    def translate(self, text):
        """
        Set all widgets insinsitive and start translation.
        After this view the new translated text and let widgets be sensitive.
        @param text: Text to be translated
        """
        self.translating = 1
        widgets = [self.w_translate, self.w_module, self.w_from, self.w_to]
        for widget in widgets:
            gtk.threads_enter()
            widget.set_sensitive(0)
            gtk.threads_leave()
        translated = self.translator.translate(text, "Text", None)
        for widget in widgets:
            gtk.threads_enter()
            widget.set_sensitive(1)
            gtk.threads_leave()
        if not self.translating: return
        gtk.threads_enter()
        if self._parent.config.getboolean('minimalist', 'popup') or not self._parent.config.getboolean('clipboard', 'set'):
            popup = MiniTranslation.Popup(self, text, translated)
            popup.run()
            popup.destroy()
        if self._parent.config.getboolean('clipboard', 'set'):
            self._parent.clipboard.set_text(translated)
            self._parent.cur_clipboard = translated
        gtk.threads_leave()
        self.translating = 0
        
    def update_trayicon_settings(self):
        if self._parent.tray:
            try:
                self.disconnect(self.h_destroy)
            except: pass
            self.h_delete = self.connect('delete-event', self.on_delete)
        else:
            try:
                self.disconnect(self.h_delete)
            except: pass
            self.h_destroy = self.connect('destroy',
                                          lambda *w: gtk.main_quit())  
        
    # Events
    
    def on_normalize(self, w):
        if self.translating and self._parent.question(_('A translation is currently running. Are you sure to close this page?')) == gtk.RESPONSE_YES or not self.translating:
            self.translating = 0
            self.hide()
            self._parent.show_all()
            self._parent.is_reduced = 0
            
    def on_translate(self, w):
        if self._parent.clipboard.wait_is_text_available():
            text = self._parent.clipboard.wait_for_text()
            if not text: return
            self._parent.clipboard.clear()
            thread.start_new_thread(self.translate, (text,))
            
    def on_show(self, w):
        self._parent.preferred_combo_module(self.w_module)

    def on_delete(self, w, Data=None):
        self._parent.tray.wnd_hide()
        return True
