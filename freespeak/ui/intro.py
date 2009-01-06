# FreeSpeak - a GUI frontend to online translator engines
# freespeak/ui/intro.py
#
## Copyright (C) 2008, 2009  Luca Bruno <lethalman88@gmail.com>
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
Introduction widgets
"""

import gtk
import gnome

from freespeak.ui.translation import TextTranslation, WebTranslation
from freespeak.ui.suggestion import TranslationSuggestions

class IntroButton (gtk.Button):
    """
    Particular button to be displayed in the introduction
    """

    def __init__ (self, text, stock):
        gtk.Button.__init__ (self)

        self.set_name ("intro-button")
        self.set_focus_on_click (False)
        self.set_relief (gtk.RELIEF_NONE)
        self.set_property ('can-focus', False)

        image = gtk.image_new_from_stock (stock, gtk.ICON_SIZE_DIALOG)
        image.show ()
        label = gtk.Label ()
        label.set_markup ("<b><u><span color='blue'>%s</span></u></b>" % text)
        label.set_alignment (0, 0.5)
        label.show ()
        hbox = gtk.HBox ()
        hbox.set_border_width (12)
        hbox.pack_start (image, False, padding=12)
        hbox.pack_start (label, False, padding=12)
        hbox.show ()
        self.add (hbox)

class Intro (gtk.Alignment):
    """
    Introduction widget containing buttons
    """

    def __init__ (self, application, manager):
        gtk.Alignment.__init__ (self, 0.5, 0.5, 0, 0)
        self.application = application
        self.manager = manager

        self.setup_layout ()
        self.setup_manager ()
        self.setup_text ()
        self.setup_web ()
        self.setup_suggestions ()
        self.setup_help ()

        self.connect ('expose-event', self.on_expose)

    def setup_layout (self):
        """
        Setup the introduction layout and create a size group to ensure
        widgets have the same horizontal size.
        """
        self.set_border_width (16)
        self.vbox = gtk.VBox (homogeneous=True)
        self.vbox.show ()
        self.add (self.vbox)
        self.size_group = gtk.SizeGroup (gtk.SIZE_GROUP_HORIZONTAL)

    def setup_manager (self):
        """
        Hide the notebook and connect to its signals
        """
        self.manager.hide ()
        self.manager.connect ('page-added', self.on_page_added)
        self.manager.connect ('page-removed', self.on_page_removed)

    def setup_text (self):
        """
        Setup the text translation button
        """
        button = IntroButton ("Make a text translation",
                              gtk.STOCK_NEW)
        button.connect ('clicked', self.on_text_clicked)
        button.show ()
        self.size_group.add_widget (button)
        self.vbox.pack_start (button)

    def setup_web (self):
        """
        Setup the web translation button
        """
        button = IntroButton ("Make a web page translation",
                              gtk.STOCK_NETWORK)
        button.connect ('clicked', self.on_web_clicked)
        button.show ()
        self.size_group.add_widget (button)
        self.vbox.pack_start (button)

    def setup_suggestions (self):
        """
        Setup the translation suggestions button
        """
        button = IntroButton ("Request translation suggestions",
                              gtk.STOCK_SELECT_FONT)
        button.connect ('clicked', self.on_suggestions_clicked)
        button.show ()
        self.size_group.add_widget (button)
        self.vbox.pack_start (button)

    def setup_help (self):
        """
        Setup the help button
        """
        button = IntroButton ("Getting started",
                              gtk.STOCK_HELP)
        button.connect ('clicked', self.on_help_clicked)
        button.show ()
        self.size_group.add_widget (button)
        self.vbox.pack_start (button)

    # Events

    def on_expose (self, widget, event):
        """
        Expose event. This will draw the introduction area to be more eye-candy.
        """
        style = self.get_style ()
        allocation = self.vbox.get_allocation ()
        _, _, width, _, _ = event.window.get_geometry ()
        _, y = 0, allocation.y-12
        _, height = allocation.width+24, allocation.height+26
        style.paint_box (event.window, gtk.STATE_PRELIGHT, gtk.SHADOW_ETCHED_IN,
                         event.area, self, None, 1, y, width-2, height)

    def on_page_added (self, *args):
        """
        Hide the introduction and show the notebook
        """
        self.hide ()
        self.manager.show ()

    def on_page_removed (self, notebook, *args):
        """
        When the notebook is empty, show the introduction and hide the notebook
        """
        if notebook.get_n_pages () == 0:
            self.manager.hide ()
            self.show ()

    def on_text_clicked (self, button):
        """
        Open a text translation tab
        """
        TextTranslation (self.application, self.manager)

    def on_web_clicked (self, button):
        """
        Open a web translation tab
        """
        WebTranslation (self.application, self.manager)

    def on_suggestions_clicked (self, button):
        """
        Open a translation suggestions tab
        """
        TranslationSuggestions (self.application, self.manager)

    def on_help_clicked (self, button):
        """
        Open the help at the 'getting-started' topic
        """
        gnome.url_show ("ghelp:freespeak?freespeak-getting-started")
