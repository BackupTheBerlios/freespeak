import gtk

class StatusIcon (gtk.StatusIcon):
    def __init__ (self, application):
        gtk.StatusIcon.__init__ (self)
        self.application = application

        self.set_from_stock (gtk.STOCK_NETWORK)

        self.connect ('activate', self.on_activate)

    def on_activate (self, *args):
        window = self.application.main_window
        if window.is_active ():
            window.set_skip_taskbar_hint (True)
            window.iconify ()
        else:
            window.present ()
            window.set_skip_taskbar_hint (False)
        
