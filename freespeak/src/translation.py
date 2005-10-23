"""
    translation.py
    Fri Jun 14 13:41:56 2004
    Copyright  2005 Italian Python User Group
    http://www.italianpug.org
   
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Library General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
"""

import gtk, thread, os, gtk.gdk
from utils import *
from progress import Progress

class TranslationBase:
    def on_module(self, widget):
        """
        Get the Translator class then insert from languages using the
        language table and set w_from widget sensitive.
        """
        itr = self.w_module.get_active_iter()
        self.translator = self.w_module.get_model().get_value(itr,
                                                              1)(self._parent)
        from_langs = []
        from_model = gtk.ListStore(str)
        for lang in self.translator.language_table:
            if lang["from"] not in from_langs:
                from_langs.append(lang["from"])
                from_model.append([lang["from"]])
        if self.translator.language_table:
            self.w_from.set_model(from_model)
            self.w_from.set_sensitive(1)
        try:
            if not self._parent.custom_tab_name:
                self._parent.tab_name = widget.get_active_text()
                self._parent.set_label_tab()
            if self._parent.translator.icon_file:
                self._parent.tab_image.set_from_file(os.path.join(
                    self._parent._parent.icons,
                    self._parent.translator.icon_file)) 
        except: pass

    
    def on_from(self, widget):
        """
        Get the languages which can be translated from the selected language
        and set w_to widget sensitive.
        """
        self.translator.from_lang = widget.get_active_text()
        to_model = gtk.ListStore(str)
        for lang in self.translator.language_table:
            if lang["from"] == widget.get_active_text():
                to_model.append([lang["to"]])

        self.w_to.set_model(to_model)
        if len(to_model) == 1:
            self.w_to.set_active(0)
        self.w_to.set_sensitive(1)
    
    def on_to(self, widget):
        """
        Translation ready to be started
        """
        self.translator.to_lang = widget.get_active_text()
        self.w_translate.set_sensitive(1)
        try:
            self.w_browser.set_sensitive(1)
        except:
            pass

class Text(gtk.VBox, TranslationBase):
    def __init__(self, parent, preferred):
        gtk.VBox.__init__(self)
        self._parent = parent
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

class Web(gtk.VBox, TranslationBase):
    def __init__(self, parent, preferred):
        gtk.VBox.__init__(self)
        self._parent = parent
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

    
class Translation(Frame):
    def __init__(self, parent, kind, preferred):
        """
        Create a new empty translation page
        """
        Frame.__init__(self)
        self._parent = parent
        self.kind = kind
        self.accel_group = self._parent.accel_group
        self.translating = 0
        self.alignment.set_padding(0, 0, 6, 6)
        
        self.tab_name = 'Unnamed'
        self.custom_tab_name = 0
        self.tab = gtk.HBox(spacing=3)
        self.tab_event = gtk.EventBox()
        self.tab_event.connect('button-press-event', self.on_tab_pressed)
        self.tab_label = gtk.Label()
        self.tab_entry = gtk.Entry()
        self.tab_entry.connect('activate', self.on_tab_renamed)
        self.entry_handler = self.tab_entry.connect("focus-out-event",
                                                    self.on_tab_focusout)
        self.tab_event.add(self.tab_label)
        self.set_label_tab()
        self.tab_image = gtk.Image()
        self.tab.pack_start(self.tab_image)
        self.tab.pack_start(self.tab_event)

        if kind == "New":
            self.page = Text(self, preferred)
        else:
            self.page = Web(self, preferred)
            self.page.w_browser.connect("clicked", self.on_browser)
            self.page.w_browser.add_accelerator('clicked', self.accel_group,
                                                ord('V'), gtk.gdk.CONTROL_MASK,
                                                gtk.ACCEL_LOCKED) 
            self.page.w_browser.add_accelerator("grab-focus", self.accel_group, 
                                                accel_key(
                _("<u>V</u>iew in browser")), 
                                                gtk.gdk.MOD1_MASK, 
                                                gtk.ACCEL_LOCKED) 
            

        self.page.w_translate.connect("clicked", self.on_translate)
        self.page.w_translate.add_accelerator('clicked', self.accel_group,
                                              ord('T'), gtk.gdk.CONTROL_MASK,
                                              gtk.ACCEL_LOCKED) 
        self.page.w_translate.add_accelerator('grab-focus', self.accel_group,
                                              accel_key(_("<u>T</u>ranslate!")),
                                              gtk.gdk.MOD1_MASK,
                                              gtk.ACCEL_VISIBLE)
        
        self.add(self.page)

        self.tab_menu = gtk.Menu()
        
        item = gtk.ImageMenuItem(gtk.STOCK_EDIT, _('Rename'))
        item.connect('button-press-event', self.on_tab_renaming)
        self.tab_menu.add(item)
        
        item = gtk.ImageMenuItem(gtk.STOCK_CLOSE, _('Close'))
        item.connect('button-press-event', self.on_close)
        
        self.tab_menu.add(item)
        self.tab_menu.show_all()
        
        close = gtk.Button()
        close.set_relief(gtk.RELIEF_NONE)
        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        close.add(img)
        close.connect('clicked', self.on_close)
        close.add_accelerator("clicked", self._parent.accel_group, ord("w"),
                              gtk.gdk.CONTROL_MASK, gtk.ACCEL_LOCKED)
        self.tab.pack_start(close)
        self.tab.show_all()
        self.tab_image.show()
        self.show_all()
        
    # Tools
    
    def translate(self, text, browser=False):
        """
        Set all widgets insinsitive and start translation.
        After this view the new translated text and let widgets be sensitive.
        @param text: Text to be translated
        """
        self.translating = 1
        widgets = [self.page.w_translate, self.page.w_module, self.page.w_from,
                   self.page.w_to, self.page.w_source] 
        for widget in widgets:
            gtk.threads_enter()
            widget.set_sensitive(0)
            gtk.threads_leave()
        translated = self.page.translator.translate(text, self.kind,
                                                    self.page.progress)
        gtk.threads_enter()
        self.page.set_result(translated, browser)
        gtk.threads_leave()
        for widget in widgets:
            gtk.threads_enter()
            widget.set_sensitive(1)
            gtk.threads_leave()
        self.translating = 0
        gtk.threads_enter()
        nb = self._parent.nb
        if nb.get_nth_page(nb.get_current_page()) != self:
            self.tab_label.set_markup('<span color="blue">'+
                                      self.tab_name+'</span>')
        self.page.progress.set_step(5)
        gtk.threads_leave()
            
    def set_label_tab(self):
        if self.entry_handler:
            self.tab_entry.disconnect(self.entry_handler)
            self.entry_handler = None
        self.tab_event.remove(self.tab_event.get_child())
        self.tab_event.add(self.tab_label)
        self.tab_label.set_text(self.tab_name)
        self.tab_label.show()
        
    def set_entry_tab(self):
        if not self.entry_handler:
            self.entry_handler = self.tab_entry.connect("focus-out-event",
                                                        self.on_tab_focusout)
        self.tab_event.remove(self.tab_event.get_child())
        self.tab_entry.set_text(self.tab_name)
        self.tab_entry.set_width_chars(len(self.tab_name))
        self.tab_entry.show()
        self.tab_event.add(self.tab_entry)
        self.tab_entry.grab_focus()

        
    def start_tab_renaming(self):
        self.set_entry_tab()
        self.custom_tab_name = 1
        
    # Events

    def on_tab_focusout(self, w, data=None):
        self.set_label_tab()
    
    def on_translate(self, widget):
        """
        Start the translation by spawning a new thread
        """
        text = self.page.get_source()
        if not text: return
        thread.start_new_thread(self.translate, (text,))

    def on_browser(self, w):
        text = self.page.get_source()
        if not text: return
        thread.start_new_thread(self.translate, (text, True))
        
    def on_close(self, *w):
        """
        Remove myself from the notebook.
        Don't care if a translation is running on.
        """
        if (self.translating and
            self._parent.question(
    _('A translation is currently running. Are you sure to close this page?'))
            == gtk.RESPONSE_YES or not self.translating): 
            self._parent.nb.remove(self)
            
    def on_tab_pressed(self, w, event):
        """
        Mouse pressed on the tab
        """
        if event.button == 1:
            if event.type == gtk.gdk.BUTTON_PRESS:
                self.tab_label.set_text(self.tab_name)
            elif event.type == gtk.gdk._2BUTTON_PRESS:
                self.start_tab_renaming()
        elif event.button == 3:
            self.tab_menu.popup(None, None, None, 0, event.time)
        
    def on_tab_renamed(self, w):
        """
        The tab as been renamed
        """
        self.tab_name = w.get_text()
        self.tab_entry.set_width_chars(len(self.tab_name))
        self.set_label_tab()
   
    def on_tab_renaming(self, w, event):
        if event.button == 1: self.start_tab_renaming()

class MiniTranslation(gtk.Window, TranslationBase):
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
        translated = self.translator.translate(text)
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
