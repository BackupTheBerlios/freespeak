# FreeSpeak - a GUI frontend to online translator engines
# freespeak/ui/utils.py
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
GUI utilities
"""

import gtk
import gobject

class ScrolledWindow (gtk.ScrolledWindow):
    """
    Create a scrolled window with particular options
    """
    def __init__ (self, child):
        gtk.ScrolledWindow.__init__ (self)
        self.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.set_shadow_type (gtk.SHADOW_ETCHED_IN)
        self.add (child)

class Frame (gtk.Frame):
    """
    HIG compliant frame
    """
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
        """
        Overridden container method to add the widget respecting the HIG
        """
        alignment = gtk.Alignment ()
        alignment.set_property ('top-padding', 6)
        alignment.set_property ('left-padding', 12)
        alignment.set_property ('xscale', 1)
        alignment.set_property ('yscale', 1)
        alignment.add (widget)
        alignment.show ()
        return gtk.Frame.add (self, alignment)

class Progress (gtk.HBox):
    """
    A progress bar to be used as a user feedback.
    The widget contains a cancellation button.
    """
    __gsignals__ = {
        'cancelled': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        }

    def __init__ (self):
        gtk.HBox.__init__ (self, spacing=6)
        self.running = False

        self.setup_bar ()
        self.setup_cancel ()

    def setup_bar (self):
        """
        Setup the progress bar
        """
        self.bar = gtk.ProgressBar ()
        self.bar.set_pulse_step (0.01)
        self.bar.show ()
        self.pack_start (self.bar)

    def setup_cancel (self):
        """
        Setup the cancellation button
        """
        self.cancel = TinyButton (gtk.STOCK_CANCEL)
        self.cancel.connect ('clicked', self.on_cancel)
        self.cancel.show ()
        self.pack_start (self.cancel, False)

    def pulse_idle (self):
        """
        GObject idle for pulsing the progress bar
        """
        self.bar.pulse ()
        return self.running

    # API

    def is_running (self):
        """
        Returns True if the progress is pulsing, False otherwise
        """
        return self.running

    def set_text (self, text):
        """
        Set the text inside the progress bar
        """
        self.bar.set_text (text)

    def start (self):
        """
        Start pulsing the progress bar
        """
        assert not self.running
        self.running = True
        gobject.timeout_add (10, self.pulse_idle)

    def stop (self):
        """
        Stop the progress
        """
        self.running = False

    # Events

    def on_cancel (self, button):
        """
        Emit the 'cancelled' signal the the cancellation button is clicked
        """
        self.emit ('cancelled')

class TinyButton (gtk.Button):
    """
    A small tiny and eye-candy button to be used beside widgets
    """
    def __init__ (self, stock=None, size=gtk.ICON_SIZE_MENU):
        gtk.Button.__init__ (self)
        self.set_name ("tiny-button")
        self.set_relief (gtk.RELIEF_NONE)
        self.set_property ('can-focus', False)
        if stock:
            image = gtk.image_new_from_stock (stock, size)
            self.set_image (image)

class MessageDialog (gtk.MessageDialog):
    """
    Convenient class for creating message dialogs
    """
    def __init__ (self, parent, message, mtype, buttons):
        flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT
        gtk.MessageDialog.__init__ (self, parent, flags, mtype, buttons, message)
        self.connect ('response', self.on_response)

    def on_response (self, dialog, response):
        """
        Destory the dialog on whatever response
        """
        dialog.destroy ()

def error (message, parent=None):
    """
    Show an error message dialog
    """
    dialog = MessageDialog (parent, message,
                            gtk.MESSAGE_ERROR, gtk.BUTTONS_OK)
    dialog.show_all ()

def warning (message, parent=None):
    """
    Show a warning message dialog
    """
    dialog = MessageDialog (parent, message,
                            gtk.MESSAGE_WARNING, gtk.BUTTONS_OK)
    dialog.show_all ()
