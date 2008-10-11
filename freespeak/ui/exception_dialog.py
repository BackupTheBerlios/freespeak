import traceback

from freespeak import ui

class ExceptionDialog (gtk.Dialog):
    """
    Show non-catched exception in a window
    """
    def __init__(self, *tb):
        gtk.Dialog.__init__ (self, 'FreeSpeak - '+_('Exception'), None, 0,
                             (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        self.set_keep_above (1)
        self.set_resizable (1)
        self.set_default_size (400, 300)
        
        label = gtk.Label()
        label.set_markup ('<span color="red"><b>'+_('An error has occurred:')+'</b></span>')
        label.show()
        self.vbox.pack_start (label, 0, 0)
        text = gtk.TextView()
        text.get_buffer().set_text (''.join (traceback.format_exception (*tb)))
        scroll = ui.ScrolledWindow (text)
        scroll.show ()
        self.vbox.pack_start (scroll)
        
        self.run ()
