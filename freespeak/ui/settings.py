# FreeSpeak - a GUI frontend to online translator engines
# freespeak/ui/settings.py
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
Handle configurations the GUI way
"""

import gtk
import gnome

from freespeak import utils
import freespeak.ui.utils as uiutils
from freespeak.ui.translation_box import TranslatorCombo

class Settings (gtk.Dialog):
    """
    A dialog allowing the user to modify configuration keys
    """

    @utils.syncronized
    def __init__(self, application):
        gtk.Dialog.__init__ (self, _('Preferences'), application.main_window, 0,
                             (gtk.STOCK_HELP, gtk.RESPONSE_HELP,
                              gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        self.application = application

        self.set_border_width (6)
        self.set_modal (True)

        self.setup_layout ()
        self.setup_clipboard ()
        self.setup_translator ()
        self.setup_keybindings ()

        self.connect ('response', self.on_response)
        self.show ()

    def setup_layout (self):
        """
        Setup the layout of the dialog.
        Create size groups for ensuring widgets have the same horizontal size.
        """
        self.vbox.set_spacing (6)
        self.left_group = gtk.SizeGroup (gtk.SIZE_GROUP_HORIZONTAL)
        self.right_group = gtk.SizeGroup (gtk.SIZE_GROUP_HORIZONTAL)

    def setup_clipboard (self):
        """
        Clipboard preferences
        """
        frame = uiutils.Frame (_('Clipboard preferences'))
        frame.show ()
        vbox = gtk.VBox (spacing=6)
        vbox.show ()

        description = _("_Get text/url from clipboard automatically")
        self.w_clipboard_get = gtk.CheckButton (description)
        value = self.application.config.get ('get_clipboard')
        self.w_clipboard_get.set_active (value)
        self.w_clipboard_get.show ()
        vbox.pack_start (self.w_clipboard_get, False)

        description = _("_Save translated text/url to clipboard")
        self.w_clipboard_set = gtk.CheckButton (description)
        value = self.application.config.get ('set_clipboard')
        self.w_clipboard_set.set_active (value)
        self.w_clipboard_set.show ()
        vbox.pack_start (self.w_clipboard_set, False)
        
        frame.add (vbox)
        frame.show ()
        self.vbox.pack_start (frame)

    def setup_translator (self):
        """
        Translators preferences
        """
        frame = uiutils.Frame (_("Translator preferences"))
        frame.show ()
        vbox = gtk.VBox (spacing=6)
        vbox.show ()
        
        hbox = gtk.HBox(spacing=12)
        hbox.show ()
        label = gtk.Label (_("_Preferred translator"))
        label.set_use_underline (True)
        label.set_alignment (0, 0.5)
        label.show ()
        self.left_group.add_widget (label)
        hbox.pack_start (label, False)
        self.w_preferred_translator = TranslatorCombo (self.application)
        default_translator = self.application.translators_manager.get_default ()
        model = self.w_preferred_translator.get_model ()
        for row in model:
            if row[TranslatorCombo.COL_TRANSLATOR] == default_translator:
                self.w_preferred_translator.set_active_iter (row.iter)
                break
        self.w_preferred_translator.show ()
        self.right_group.add_widget (self.w_preferred_translator)
        label.set_mnemonic_widget (self.w_preferred_translator)
        hbox.pack_start (self.w_preferred_translator)
        vbox.pack_start (hbox)
        
        frame.add (vbox)
        frame.show ()
        self.vbox.pack_start (frame)

    def setup_keybindings (self):
        """
        Global keybindings preferences
        """
        frame = uiutils.Frame (_('Key bindings'))
        frame.show ()
        vbox = gtk.VBox (spacing=6)
        vbox.show ()

        hbox = gtk.HBox(spacing=12)
        hbox.show ()
        label = gtk.Label (_("_Translate from clipboard"))
        label.set_use_underline (True)
        label.set_alignment (0, 0.5)
        label.show ()
        self.left_group.add_widget (label)
        hbox.pack_start (label, False)
        model = gtk.ListStore (int, int, bool)
        accelerator = self.application.config.get ("key_binding")
        keyval, modifiers = gtk.accelerator_parse (accelerator)
        model.append ([keyval, modifiers, True])
        self.w_key_binding = gtk.TreeView ()
        self.w_key_binding.set_model (model)
        renderer = gtk.CellRendererAccel ()
        renderer.connect ('accel-edited', self.on_key_binding_edited)
        renderer.connect ('accel-cleared', self.on_key_binding_cleared)
        column = gtk.TreeViewColumn (None, None)
        column.pack_start (renderer, True)
        column.set_attributes (renderer, accel_key=0, accel_mods=1, editable=2)
        self.w_key_binding.append_column (column)
        self.w_key_binding.set_headers_visible (False)
        # Having a white background is ugly
        self.w_key_binding.get_selection().select_iter (model[0].iter)
        # Grab keyboard focus when clicked,
        # otherwise the user can't set the accel (GTK+ bug?)
        self.w_key_binding.connect ('button-press-event',
                                    self.on_key_binding_press)
        self.w_key_binding.show ()
        self.right_group.add_widget (self.w_key_binding)

        hbox.pack_start (self.w_key_binding)
        vbox.pack_start (hbox)
        
        frame.add (vbox)
        frame.show ()
        self.vbox.pack_start (frame)

    # Events

    def on_key_binding_edited (self, renderer, path,
                               keyval, modifiers, keycode):
        """
        Set the new key binding
        """
        row = self.w_key_binding.get_model()[0]
        row[0] = keyval
        row[1] = modifiers
        self.application.config.set ("key_binding",
                                     gtk.accelerator_name (keyval, modifiers))

    def on_key_binding_cleared (self, renderer, path):
        """
        Disable the key binding
        """
        row = self.w_key_binding.get_model()[0]
        row[0] = 0
        row[1] = 0
        self.application.config.set ("key_binding", "disabled")

    def on_key_binding_press (self, *args):
        """
        The treeview has been pressed.
        This is an hack as GTK+ doesn't give focus to the treeview when the
        AccelCell has been selected.
        """
        self.w_key_binding.grab_focus ()

    def on_response (self, dialog, response):
        """
        Dialog response will open the Help if necessary, otherwise save the
        configuration.
        """
        if response == gtk.RESPONSE_HELP:
            gnome.url_show ("ghelp:freespeak?freespeak-prefs")
            return

        self.application.config.set ('get_clipboard',
                                     self.w_clipboard_get.get_active ())
        self.application.config.set ('set_clipboard',
                                     self.w_clipboard_set.get_active ())
        translator = self.w_preferred_translator.get_active_translator ()
        if translator:
            self.application.config.set ('default_translator',
                                         translator.module_name)
        else:
            self.application.config.set ('default_translator', '')
        self.destroy()

