# FreeSpeak - a GUI frontend to online translator engines
# freespeak/ui/exception_dialog.py - this file is part of FreeSpeak
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

import traceback
import sys

import gtk

from freespeak.ui import utils as uiutils
from freespeak import utils

# FIXME:
# 1. Needs HIG pixel fixes
# 2. Error icon dialog
# 3. Use an expander to show more details on the traceback

class ExceptionDialog (gtk.Dialog):
    @utils.syncronized
    def __init__(self, error_string):
        gtk.Dialog.__init__ (self, 'FreeSpeak - '+_('Exception'), None, 0,
                             (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        self.set_keep_above (1)
        self.set_resizable (1)
        self.set_default_size (400, 300)
        self.set_border_width (6)
        self.set_default_response (gtk.RESPONSE_CLOSE)

        self.vbox.set_spacing (6)
        
        label = gtk.Label()
        label.set_markup ('<span color="red"><b>'+_('An error has occurred:')+'</b></span>')
        label.show()
        self.vbox.pack_start (label, False)
        text = gtk.TextView()
        text.show ()
        text.get_buffer().set_text (error_string)
        text.set_editable (False)
        scroll = uiutils.ScrolledWindow (text)
        scroll.show ()
        self.vbox.pack_start (scroll)
        self.vbox.show ()

        self.connect ('response', self.on_response)
        self.show_all ()

    def on_response (self, dialog, *args):
        dialog.destroy ()

def exception_hook (*tb):
    error_string = ''.join (traceback.format_exception (*tb))
    print >> sys.stderr, error_string
    ExceptionDialog (error_string)

