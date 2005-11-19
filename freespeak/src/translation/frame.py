from web import WebTranslation
from text import TextTranslation
import gtk, gtk.gdk
import thread
from src.utils import *
from src.progress import Progress
    
class Translation(Frame):
    def __init__(self, parent, kind, preferred):
        """
        Create a new empty translation page
        """
        Frame.__init__(self)
        self._parent = parent
        self.page = None
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

        if kind == "Text":
            self.page = TextTranslation(self, preferred)
        else:
            self.page = WebTranslation(self, preferred)
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
