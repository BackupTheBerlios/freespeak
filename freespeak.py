#!/usr/bin/env python
"""
    freespeak.py
    Fri Jun 14 13:41:56 2004
    Copyright  2005 Italian Python User Group
    http://www.italianpug-org
   
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

import gtk, gtk.gdk, os, sys, gettext, thread
from ConfigParser import ConfigParser
gettext.NullTranslations()
gettext.install('freespeak')

ui_string = """<ui>
<toolbar>
    <toolitem action="New" />
    <toolitem action="Settings" />
    <separator />
    <toolitem action="Quit" />
    <toolitem action="About" />
    <separator />
</toolbar>
</ui>"""

def make_combo():
    """
    Create a ComboBox with a simple text renderer
    @return: ComboBox
    """
    combo = gtk.ComboBox()
    renderer = gtk.CellRendererText()
    combo.pack_start(renderer)
    combo.add_attribute(renderer, 'text', 0)
    return combo
    
def make_text(widget):
    """
    Return a scrolled window with a given widget inside
    @param widget: The widget tu put inside the scrolled window
    @return: ScrolledWindow
    """
    sw = gtk.ScrolledWindow()
    sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    sw.set_border_width(2)
    sw.set_shadow_type(gtk.SHADOW_IN)
    sw.add(widget)
    return sw
    
def make_button(text, stock):
    """
    Make a button specifying its text label and stock icon
    @param label: The text of the button
    @param stock: Personalized stock item
    @return: Button
    """
    btn = gtk.Button()
    align = gtk.Alignment(0.5, 0.5)
    hbox = gtk.HBox(spacing=2)
    img = gtk.Image()
    img.set_from_stock(stock, gtk.ICON_SIZE_BUTTON)
    hbox.pack_start(img, 0)
    label = gtk.Label()
    label.set_markup(text)
    hbox.pack_start(label, 0)
    align.add(hbox)
    btn.add(align)
    return btn


class Config(ConfigParser):
    def __init__(self):
        """
        Open existing config file or create one in the user home directory.
        """
        ConfigParser.__init__(self)
        import user
        self.file = user.home+os.sep+'.freespeak'
        try:
            self.readfp(file(self.file))
        except:
            self.add_section('clipboard')
            self.set('clipboard', 'get', 'no')
            self.set('clipboard', 'set', 'no')
            self.save()
    
    def save(self):
        self.write(file(self.file, 'w'))
    
class Win_Settings(gtk.Dialog):
    def __init__(self, parent):
        """
        FreeSpeak user preferences
        """
        gtk.Dialog.__init__(self, 'FreeSpeak - '+_('Settings'), parent, 0,
                (gtk.STOCK_OK, gtk.RESPONSE_OK,
                gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        self._parent = parent
        config = parent.config
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_border_width(3)
        self.vbox.set_spacing(3)
        
        frame = gtk.Frame(_('Clipboard preferences'))
        frame.set_border_width(3)
        vbox = gtk.VBox(spacing=3)
        
        self.w_clipboard_get = gtk.CheckButton(_('Get text from clipboard automatically'))
        self.w_clipboard_get.set_active(config.getboolean('clipboard', 'get'))
        vbox.pack_start(self.w_clipboard_get, 0, 0)
        self.w_clipboard_set = gtk.CheckButton(_('Save text to clipboard after translation'))
        self.w_clipboard_set.set_active(config.getboolean('clipboard', 'set'))
        vbox.pack_start(self.w_clipboard_set, 0, 0)
        
        frame.add(vbox)
        frame.show_all()
        self.vbox.pack_start(frame)

    def start(self):
        if self.run() == gtk.RESPONSE_CANCEL:
            self.destroy()
            return
        config = self._parent.config
        for setting in ((self.w_clipboard_get, 'get'), (self.w_clipboard_set, 'set')):
            if setting[0].get_active(): config.set('clipboard', setting[1], 'yes')
            else: config.set('clipboard', setting[1], 'no')
        config.save()
        self.destroy()
    
class Translation(gtk.Frame):
    def __init__(self, parent):
        """
        Create a new empty translation page
        """
        gtk.Frame.__init__(self)
        self._parent = parent
        self.translating = 0
        self.set_border_width(3)
        
        vbox = gtk.VBox(spacing=3)
        hbox = gtk.HBox(spacing=3)
        
        hbox.pack_start(gtk.Label(_('Translation:')), 0, 0)
        self.w_module = make_combo()
        hbox.pack_start(self.w_module)
        
        hbox.pack_start(gtk.Label(_('From:')), 0, 0)
        self.w_from = make_combo()
        self.w_from.set_sensitive(0)
        hbox.pack_start(self.w_from)
        
        hbox.pack_start(gtk.Label(_('To:')), 0, 0)
        self.w_to = make_combo()
        self.w_to.set_sensitive(0)
        hbox.pack_start(self.w_to)
     
        self.w_translate = make_button('<u>T</u>ranslate!', gtk.STOCK_REFRESH)
        self.w_translate.set_sensitive(0)
        hbox.pack_start(self.w_translate, 0, 0)
        vbox.pack_start(hbox, 0, 0)

        buffer = gtk.TextBuffer() 
        if self._parent.config.getboolean('clipboard', 'get') and self._parent.clipboard.wait_is_text_available():
            text = self._parent.clipboard.wait_for_text()
            if text != self._parent.cur_clipboard:
                buffer.paste_clipboard(self._parent.clipboard, None, 1)
                self._parent.cur_clipboard = text
                self._parent.clipboard.clear()
        self.w_textfrom = gtk.TextView(buffer)
        vbox.pack_start(make_text(self.w_textfrom))
        vbox.pack_start(gtk.HSeparator(), 0, 0)
        self.w_textto = gtk.TextView()
        vbox.pack_start(make_text(self.w_textto))
        
        module_model = gtk.ListStore(str, object)
        for module in os.listdir('modules'):
            if module == '__init__.py' or module[-3:] == 'pyc': continue
            try:
                imported_module = getattr(__import__('modules.'+module[:-3]), module[:-3])
                imported_module.name
                translator = imported_module.Translator
                translator.build_language_table, translator.translate
                module_model.append([imported_module.name, translator])
            except: pass
        self.w_module.set_model(module_model)
        self.w_module.connect("changed", self.on_module)
        self.w_from.connect("changed", self.on_from)
        self.w_to.connect("changed", self.on_to)
        self.w_translate.connect("clicked", self.on_translate)
        accel = gtk.AccelGroup()
        self.w_translate.add_accelerator('clicked', accel, ord('T'), gtk.gdk.CONTROL_MASK, 0)
        self._parent.add_accel_group(accel)
        self.add(vbox)
        
        self.tab_name = 'Unnamed'
        self.tab = gtk.HBox(spacing=3)
        self.tab_event = gtk.EventBox()
        self.tab_event.connect('button-press-event', self.on_tab_rename)
        self.tab_label = gtk.Label()
        self.tab_entry = gtk.Entry()
        self.tab_entry.connect('changed', self.on_tab_changed)
        self.tab_entry.connect('activate', self.on_tab_renamed)
        self.tab_event.add(self.tab_label)
        self.set_label_tab()
        self.tab.pack_start(self.tab_event)
        
        close = gtk.Button()
        close.set_relief(gtk.RELIEF_NONE)
        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        close.add(img)
        close.connect('clicked', self.on_close)
        self.tab.pack_start(close)
        self.tab.show_all()
        
        self.show_all()
        
    # Tools
    
    def translate(self, text):
        """
        Set all widgets insinsitive and start translation.
        After this view the new translated text and let widgets be sensitive.
        @param text: Text to be translated
        """
        self.translating = 1
        widgets = [self.w_translate, self.w_module, self.w_from, self.w_to, self.w_textfrom]
        for widget in widgets:
            gtk.threads_enter()
            widget.set_sensitive(0)
            gtk.threads_leave()
        translated = self.translator.translate(text)
        a = translated
        translated = unicode(translated, "iso8859-15")     
        translated = translated.encode('utf-8')
        gtk.threads_enter()
        buffer = gtk.TextBuffer()
        buffer.set_text(translated)
        self.w_textto.set_buffer(buffer)
        if self._parent.config.getboolean('clipboard', 'set'):
            self._parent.clipboard.set_text(translated)
            self._parent.cur_clipboard = translated
        gtk.threads_leave()
        for widget in widgets:
            gtk.threads_enter()
            widget.set_sensitive(1)
            gtk.threads_leave()
        self.translating = 0
        
    def set_label_tab(self):
        self.tab_event.remove(self.tab_event.get_child())
        self.tab_event.add(self.tab_label)
        self.tab_label.set_text(self.tab_name)
        self.tab_label.show()
        
    def set_entry_tab(self):
        self.tab_event.remove(self.tab_event.get_child())
        self.tab_entry.set_text(self.tab_name)
        self.tab_entry.set_width_chars(len(self.tab_name))
        self.tab_entry.show()
        self.tab_event.add(self.tab_entry)
        
    # Events
        
    def on_module(self, widget):
        """
        Get the Translator class then insert from languages using the language table
        and set w_from widget sensitive.
        """
        itr = self.w_module.get_active_iter()
        self.translator = self.w_module.get_model().get_value(itr, 1)(self._parent)
        from_langs = []
        from_model = gtk.ListStore(str)
        for lang in self.translator.language_table:
            if lang["from"] not in from_langs:
                from_langs.append(lang["from"])
                from_model.append([lang["from"]])
        self.w_from.set_model(from_model)
        self.w_from.set_sensitive(1)
    
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
        self.w_to.set_sensitive(1)
    
    def on_to(self, widget):
        """
        Translation ready to be started
        """
        self.translator.to_lang = widget.get_active_text()
        self.w_translate.set_sensitive(1)
        
    def on_translate(self, widget):
        """
        Start the translation by spawning a new thread
        """
        buffer = self.w_textfrom.get_buffer()
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter())
        if not text: return
        thread.start_new_thread(self.translate, (text,))
        
    def on_close(self, w):
        """
        Remove myself from the notebook.
        Don't care if a translation is running on.
        """
        if self.translating and self._parent.question(_('A translation is currently running. Are you sure to close this page?')) == gtk.RESPONSE_YES or not self.translating:
            self._parent.nb.remove(self)
            
    def on_tab_rename(self, w, event):
        """
        Rename the tab name with a left double click
        """
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1: self.set_entry_tab()
        
    def on_tab_renamed(self, w):
        """
        The tab as been renamed
        """
        self.set_label_tab()

    def on_tab_changed(self, w):
        self.tab_name = w.get_text()
        self.tab_entry.set_width_chars(len(self.tab_name))

class Win_Main(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.config = Config()
        self.clipboard = gtk.Clipboard()
        self.cur_clipboard = ''
        self.set_title('FreeSpeak 0.1')
        self.set_border_width(3)
        self.connect('delete-event', self.on_delete)
        self.connect('destroy', lambda *w: gtk.main_quit())
        self.resize(500, 400)
        
        vbox = gtk.VBox(spacing=3)
        ag = gtk.ActionGroup('WindowActions')
        actions = (
            ('New', gtk.STOCK_NEW, _('New'), None, _('New translation'), self.on_new),
            ('Settings', gtk.STOCK_PREFERENCES, _('Settings'), None, _('FreeSpeak settings'), self.on_settings),
            ('Quit', gtk.STOCK_QUIT, _('Quit'), None, _('Quit FreeSpeak'), self.on_delete),
            ('About', gtk.STOCK_ABOUT, _('About'), None, _('About FreeSpeak'), self.on_about),
        )
        ag.add_actions(actions)
        ui = gtk.UIManager()
        ui.insert_action_group(ag, 0)
        ui.add_ui_from_string(ui_string)
        self.add_accel_group(ui.get_accel_group())
        vbox.pack_start(ui.get_widget("/toolbar"), 0)
        self.nb = gtk.Notebook()
        self.nb.set_scrollable(1)
        vbox.pack_start(self.nb)
        
        self.add(vbox)
        self.show_all()
        
    # Tools
    
    def error(self, message, parent=None):
        """
        Run an message dialog for an error
        """
        if not parent: parent = self
        dialog = gtk.MessageDialog(parent,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, message)
        dialog.run()
        dialog.destroy()
        
    def question(self, msg, parent=None):
        """
        Ask a question and return the response of the message dialog
        @param msg: The message to be shown
        @param parent: Specify the transient parent
        @return: Dialog response
        """
        if not parent: parent = self
        dialog = gtk.MessageDialog(parent,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_QUESTION, gtk.BUTTONS_NONE, msg)
        dialog.add_buttons(gtk.STOCK_YES, gtk.RESPONSE_YES,
            gtk.STOCK_NO, gtk.RESPONSE_NO) 
        dialog.set_default_response(gtk.RESPONSE_NO)
        response = dialog.run()
        dialog.destroy()
        return response
        
    # Events
        
    def on_delete(self, *w):
        """
        Still unimplemented. Maybe use this for asking questions when quitting
        to save sessions.
        """
        self.destroy()
        
    def on_new(self, w):
        """
        Open a new tab in the notebook and start a new translation
        """
        translator = Translation(self)
        self.nb.append_page(translator, translator.tab)
        self.nb.set_current_page(self.nb.get_n_pages()-1)
        
    def on_settings(self, w):
        """
        FreeSpeak preferences
        """
        Win_Settings(self).start()
        
    def on_about(self, w):
        """
        Open an AboutDialog for this software
        """
        pass        
        
os.chdir(os.path.dirname(sys.argv[0]))

gtk.threads_init()
Win_Main()
gtk.threads_enter()
gtk.main()
gtk.threads_leave()
