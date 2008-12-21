import gtk

class IntroButton (gtk.Button):
    def __init__ (self, text, description, stock):
        gtk.Button.__init__ (self, text)

        self.set_name ("intro-button")
        self.set_relief (gtk.RELIEF_NONE)
        self.set_property ('can-focus', False)
        image = gtk.image_new_from_stock (stock, gtk.ICON_SIZE_DIALOG)
        self.set_image (image)

class Intro (gtk.VBox):
    def __init__ (self, application, manager):
        gtk.VBox.__init__ (self, homogeneous=True)
        self.application = application
        self.manager = manager

        self.setup_manager ()
        self.setup_text ()
        self.setup_web ()
        self.setup_suggestions ()
        self.setup_help ()

    def setup_manager (self):
        self.manager.hide ()
        self.manager.connect ('page-added', self.on_page_added)
        self.manager.connect ('page-removed', self.on_page_removed)

    def setup_text (self):
        button = IntroButton ("Make a text translation", "", gtk.STOCK_NEW)
        button.show ()
        self.pack_start (button)

    def setup_web (self):
        button = IntroButton ("Make a web page translation", "", gtk.STOCK_NETWORK)
        button.show ()
        self.pack_start (button)

    def setup_suggestions (self):
        button = IntroButton ("Request translation suggestions", "", gtk.STOCK_SELECT_FONT)
        button.show ()
        self.pack_start (button)

    def setup_help (self):
        button = IntroButton ("Getting started", "Getting started", gtk.STOCK_HELP)
        button.show ()
        self.pack_start (button)

    # Events

    def on_page_added (self, *args):
        self.hide ()
        self.manager.show ()

    def on_page_removed (self, notebook, *args):
        if notebook.get_n_pages () == 0:
            self.manager.hide ()
            self.show ()
