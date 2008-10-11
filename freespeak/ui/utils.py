import gtk

class ScrolledWindow (gtk.ScrolledWindow):
    def __init__ (self, child):
        gtk.ScrolledWindow.__init__ (self)
        self.add (child)
