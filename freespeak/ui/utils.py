# FreeSpeak - a GUI frontend to online translator engines
# freespeak/ui/utils.py - this file is part of FreeSpeak
#
## Copyright (C) 2005-2008  Luca Bruno <lethalman88@gmail.com>
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
## Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import gtk
import gobject

class ScrolledWindow (gtk.ScrolledWindow):
    def __init__ (self, child):
        gtk.ScrolledWindow.__init__ (self)
        self.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.set_shadow_type (gtk.SHADOW_ETCHED_IN)
        self.add (child)

class Frame (gtk.Frame):
    def __init__ (self, label_text, extra_widget=None):
        gtk.Frame.__init__ (self)
        widget = label = gtk.Label ()
        label.set_markup ("<b>"+label_text+"</b>")
        label.show ()
        if extra_widget:
            widget = gtk.HBox (spacing=6)
            widget.pack_start (label, False)
            widget.pack_start (extra_widget, False)
            widget.show ()
        self.set_property ('label-xalign', 0)
        self.set_label_widget (widget)
        self.set_shadow_type (gtk.SHADOW_NONE)

    def add (self, widget):
        alignment = gtk.Alignment ()
        alignment.set_property ('top-padding', 6)
        alignment.set_property ('left-padding', 12)
        alignment.set_property ('xscale', 1)
        alignment.set_property ('yscale', 1)
        alignment.add (widget)
        alignment.show ()
        return gtk.Frame.add (self, alignment)

class Progress (gtk.ProgressBar):
    def __init__ (self):
        gtk.ProgressBar.__init__ (self)
        self.running = False
        self.set_pulse_step (0.01)

    def pulse_idle (self):
        self.pulse ()
        return self.running

    def start (self):
        assert not self.running
        self.running = True
        gobject.timeout_add (10, self.pulse_idle)

    def stop (self):
        self.running = False

class TinyButton (gtk.Button):
    def __init__ (self, stock=None, size=gtk.ICON_SIZE_MENU):
        gtk.Button.__init__ (self)
        self.set_name ("tiny-button")
        self.set_relief (gtk.RELIEF_NONE)
        self.set_property ('can-focus', False)
        if stock:
            image = gtk.image_new_from_stock (stock, size)
            self.set_image (image)

class MessageDialog (gtk.MessageDialog):
    def __init__ (self, parent, message, type, buttons):
        gtk.MessageDialog.__init__ (self, parent, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                    type, buttons, message)
        self.connect ('response', self.on_response)

    def on_response (self, dialog, response):
        dialog.destroy ()

def error (message, parent=None):
    dialog = MessageDialog (parent, message, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK)
    dialog.show_all ()

def warning (message, parent=None):
    dialog = MessageDialog (parent, message, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK)
    dialog.show_all ()
