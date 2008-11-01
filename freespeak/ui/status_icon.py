import gtk

class StatusIcon (gtk.StatusIcon):
    def __init__ (self, window):
        gtk.StatusIcon.__init__ (self)
        self.window = window

        self.set_from_stock (gtk.STOCK_NETWORK)

        self.connect ('activate', self.on_activate)

    def on_activate (self, *args):
        if self.window.is_active ():
            self.tray ()
        else:
            self.untray ()
        
    def tray (self):
        self.window.set_skip_taskbar_hint (True)
        self.window.iconify ()

    def untray (self):
        self.window.present ()
        self.window.set_skip_taskbar_hint (False)
