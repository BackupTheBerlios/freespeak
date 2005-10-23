"""
    settings.py
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

import gtk, gtk.gdk, os.path
from src.utils import *

class Settings(gtk.Dialog):
    def add_accelerator(self, w, text):
        w.add_accelerator("grab-focus", self.accel_group, accel_key(text),
                          gtk.gdk.MOD1_MASK, gtk.ACCEL_VISIBLE)
        
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
        self.set_border_width(4)
        self.accel_group = gtk.AccelGroup()
        self.add_accel_group(self.accel_group)
        self.vbox.set_spacing(9)

        frame=Frame(_('Clipboard preferences'))
        vbox = gtk.VBox(spacing=6)

        self.w_clipboard_get = make_checkbutton(
            _('<u>G</u>et text from clipboard automatically'))
        self.w_clipboard_get.set_active(config.getboolean('clipboard', 'get'))
        self.add_accelerator(self.w_clipboard_get,
                             _('<u>G</u>et text from clipboard automatically'))
        vbox.pack_start(self.w_clipboard_get, 0, 0)

        self.w_clipboard_set = make_checkbutton(
            _('<u>S</u>ave translated text to clipboard'))
        self.w_clipboard_set.set_active(config.getboolean('clipboard', 'set'))
        self.add_accelerator(self.w_clipboard_set,
                             _('<u>S</u>ave translated text to clipboard'))
        vbox.pack_start(self.w_clipboard_set, 0, 0)
        
        frame.add(vbox)
        frame.show_all()
        self.vbox.pack_start(frame)

        frame = Frame(_("Translator preferences"))
        vbox = gtk.VBox(spacing=6)
        
        hbox = gtk.HBox(spacing=4)
        hbox.pack_start(make_label(_("<u>P</u>referred Translator")), 0 ,0)
        self.w_preferred_translator = self._parent.make_combo_modules()
        
        preferred_translator = self._parent.config.get("translator",
                                                       "preferred")     
        for row in self.w_preferred_translator.get_model():
            if row[0] == preferred_translator:
                self.w_preferred_translator.set_active_iter(row.iter)
        self.add_accelerator(self.w_preferred_translator,
                             _("<u>P</u>referred Translator"))
        hbox.pack_start(self.w_preferred_translator, 1 ,1)
        vbox.pack_start(hbox)
        
        self.w_always_top = make_checkbutton(
            _('<u>K</u>eep translator always on top'))
        self.w_always_top.set_active(config.getboolean('translator',
                                                       'alwaysontop'))
        self.add_accelerator(self.w_always_top,
                             _('<u>K</u>eep translator always on top'))
        vbox.pack_start(self.w_always_top)
        
        frame.add(vbox)
        frame.show_all()
        self.vbox.pack_start(frame)
        
        frame = Frame(_('Minimalist translator preferences'))
        vbox = gtk.VBox(spacing=6)
        
        self.w_mini_startup = make_checkbutton(
            _('Startup with <u>M</u>inimalist Translator Window'))
        self.w_mini_startup.set_active(config.getboolean('minimalist',
                                                         'startup'))
        self.add_accelerator(self.w_mini_startup,
                        _('Startup with <u>M</u>inimalist Translator Window'))
        vbox.pack_start(self.w_mini_startup)
        
        self.w_mini_popup = make_checkbutton(
            _('Show translated text in a <u>P</u>opup Window'))
        self.w_mini_popup.set_active(config.getboolean('minimalist', 'popup'))
        self.w_clipboard_set.connect('toggled', self.on_sensitive,
                                     self.w_mini_popup, 'minimalist', 'popup')
        if not self.w_clipboard_set.get_active():
            self.w_mini_popup.set_active(1)
            self.w_mini_popup.set_sensitive(0)
        else:
            self.w_mini_popup.set_active(config.getboolean('minimalist',
                                                           'popup'))
        self.add_accelerator(self.w_mini_popup,
                             _('Show translated text in a <u>P</u>opup Window'))
        vbox.pack_start(self.w_mini_popup)
        
        frame.add(vbox)
        frame.show_all()
        self.vbox.pack_start(frame)


        frame = Frame(_('Interface preferences'))
        table = gtk.Table(2, 2, False)
        table.set_col_spacings(4)
        table.set_row_spacings(6)

        label = make_label(_("<u>L</u>anguage"))
        table.attach(label, 0, 1, 0, 1, gtk.FILL, 0)
        label.set_alignment(0, 0.5)
        self.w_language = gtk.ComboBox()
        text = gtk.CellRendererText()
        icon = gtk.CellRendererPixbuf()
        self.w_language.pack_start(icon, 0)
        self.w_language.pack_start(text)
        self.w_language.add_attribute(text, 'text', 0)
        self.w_language.set_cell_data_func(icon, self.load_icon) 
        language_model = gtk.ListStore(str) 
        language_model.append(["System Default"])
        
        for language in self._parent.locale.get_list():
            try:
                language_model.append([language])
            except: pass
        self.w_language.set_model(language_model)
            
        language = self._parent.config.get("interface", "language")     
        for row in self.w_language.get_model():
            if row[0] == language:
                self.w_language.set_active_iter(row.iter)

        self.add_accelerator(self.w_language, _("<u>L</u>anguage"))
        table.attach(self.w_language, 1, 2, 0, 1)

        label = make_label(_("Toolbar <u>b</u>utton labels"))
        table.attach(label, 0, 1, 1, 2, gtk.FILL, 0)
        label.set_alignment(0, 0.5)
        self.w_toolbar = gtk.ComboBox()
        text = gtk.CellRendererText()
        self.w_toolbar.pack_start(text)
        self.w_toolbar.add_attribute(text, 'text', 0)
        model = gtk.ListStore(str)
        model.append([_("System Default")])
        model.append([_("Text and Icons")])
        model.append([_("Icons only")])
        model.append([_("Text only")])
        self.w_toolbar.set_model(model)
        self.w_toolbar.set_active(
            int(self._parent.config.get("interface", "toolbar")))

        self.add_accelerator(self.w_toolbar, _("Toolbar <u>b</u>utton labels"))
        table.attach(self.w_toolbar, 1, 2, 1, 2)

        frame.add(table)
        frame.show_all()
        self.vbox.pack_start(frame)


        frame = Frame(_('Miscellaneous preferences'))
        vbox = gtk.VBox(spacing=6)
        
        self.w_trayicon = make_checkbutton(_('Use Tray <u>I</u>con'))
        self.w_trayicon.set_active(config.getboolean('miscellaneous',
                                                     'trayicon'))
        self.add_accelerator(self.w_trayicon, _('Use Tray <u>I</u>con'))
        vbox.pack_start(self.w_trayicon)
      
        frame.add(vbox)
        frame.show_all()
        self.vbox.pack_start(frame)

    def load_icon(self, celllayout, cell, model, iter, user_data=None):
        try:
            icon = "%s%s%s.png" % (self._parent.icons, os.path.sep,
                                   model.get_value(iter, 0))
            pixbuf= gtk.gdk.pixbuf_new_from_file(icon)
            cell.set_property('pixbuf', pixbuf)
        except: pass
        return
    
    def start(self):
        if self.run() == gtk.RESPONSE_CANCEL:
            self.destroy()
            return
        config = self._parent.config
        def checkbox(widget, section, value):
            if widget.get_active(): config.set(section, value, 'yes')
            else: config.set(section, value, 'no')
        # Clipboard
        checkbox(self.w_clipboard_get, 'clipboard', 'get')
        checkbox(self.w_clipboard_set, 'clipboard', 'set')
        # Translator
        config.set("translator", "preferred",
                   self.w_preferred_translator.get_active_text())
        checkbox(self.w_always_top, 'translator', 'alwaysontop')
        self._parent.set_keep_above(self.w_always_top.get_active())
        # Minimalist
        checkbox(self.w_mini_startup, 'minimalist', 'startup')
        if self.w_mini_popup.get_property('sensitive'):
            checkbox(self.w_mini_popup, 'minimalist', 'popup')
        # Interface
        if config.get("interface", "language") != \
               self.w_language.get_active_text():
            w_dialog = gtk.MessageDialog(self, gtk.DIALOG_MODAL,
                                         gtk.MESSAGE_INFO,
                                         gtk.BUTTONS_OK,
                                _("Restart FreeSpeak to apply language changes")
                                         )
            if w_dialog.run():
                w_dialog.destroy()
        config.set("interface", "language", self.w_language.get_active_text())

        config.set("interface", "toolbar", str(self.w_toolbar.get_active()))
        self._parent.set_toolbar_style(self.w_toolbar.get_active())

        # Miscellaneous
        checkbox(self.w_trayicon, 'miscellaneous', 'trayicon')
        if self.w_trayicon.get_active():
            try:
                self._parent.create_trayicon()
            except: pass
        else:
            self._parent.remove_trayicon()
        self._parent.reduced.update_trayicon_settings()
        
        config.save()
        self.destroy()
    
    # Events
    
    def on_sensitive(self, w1, w2, section, option):
        if w1.get_active():
            w2.set_sensitive(1)
            w2.set_active(self._parent.config.getboolean(section, option))
        else:
            w2.set_sensitive(0)
            w2.set_active(1)
