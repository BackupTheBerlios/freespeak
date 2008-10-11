import traceback
import sys

import gtk

from freespeak.ui import utils

# FIXME:
# 1. Needs HIG pixel fixes
# 2. Error icon dialog
# 3. Use an expander to show more details on the traceback

class ExceptionDialog (gtk.Dialog):
    """
    Show non-catched exception in a window
    """
    def __init__(self, *tb):
        error_string = ''.join (traceback.format_exception (*tb))
        print >> sys.stderr, error_string

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
        scroll = utils.ScrolledWindow (text)
        scroll.show ()
        self.vbox.pack_start (scroll)
        self.vbox.show ()

        self.run ()
