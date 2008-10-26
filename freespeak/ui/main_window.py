import gtk
import os

from freespeak.ui.manager import *
from freespeak.ui.translation import *

class MainWindow (gtk.Window):
    ui_string = """<ui>
        <toolbar>
            <toolitem action="Text" />
            <toolitem action="Web" />
            <separator />
            <toolitem action="Settings" />
            <separator />
            <toolitem action="Quit" />
            <toolitem action="About" />
            <separator />
        </toolbar>
        <accelerator action="Text" />
        <accelerator action="Web" />
        <accelerator action="Settings" />
        <accelerator action="Quit" />
        <accelerator action="About" />
        </ui>"""
                
    def __init__(self, application):
        gtk.Window.__init__ (self)
        self.application = application

        self.setup_clipboard ()
        self.setup_window ()
        self.setup_layout ()

    def setup_clipboard (self):
        self.clipboard = gtk.Clipboard()
        self.cur_clipboard = ''

    def setup_window (self):
        self.set_title ('FreeSpeak '+self.application.version)
        self.set_border_width (6)
        self.set_default_size (500, 400)
       
        icon = os.path.join (self.application.icons_path, "freespeak-16x16.png")
        if os.path.isfile (icon):
            self.set_icon_from_stock (icon)

    def setup_layout (self):
        self.layout = gtk.VBox ()

        ag = gtk.ActionGroup ('WindowActions')
        actions = (
            ('Text', gtk.STOCK_NEW, _('_Text'), "<Control>t",
             _('New translation'), self.on_new),
            ('Web', gtk.STOCK_NETWORK, _('_Web'), "<Control>w",
             _('New web page translation'), self.on_new),
            ('Settings', gtk.STOCK_PREFERENCES, _('_Settings'),
             "<Control>s", _('FreeSpeak settings'), self.on_settings),
            ('Quit', gtk.STOCK_QUIT, _('_Quit'), "<Control>q",
             _('Quit FreeSpeak'), self.on_quit),
            ('About', gtk.STOCK_ABOUT, _('About'), "<Control>a",
             _('About FreeSpeak'), self.on_about),
            )
        ag.add_actions (actions)
        self.ui = gtk.UIManager ()
        self.ui.insert_action_group (ag, 0)
        self.ui.add_ui_from_string (self.ui_string)
        self.accel_group = self.ui.get_accel_group ()
        self.add_accel_group (self.accel_group)

        self.setup_toolbar ()
        self.setup_manager ()

        self.layout.show ()
        self.add (self.layout)

    def setup_toolbar (self):
        self.toolbar = self.ui.get_widget ("/toolbar")
        self.toolbar.show ()
        self.layout.pack_start (self.toolbar, False)

    def setup_manager (self):
        self.manager = Manager (self.application)
        self.manager.show ()
        self.layout.pack_start (self.manager)
            
    # Events
        
    def on_new(self, w):
        """
        Open a new tab in the notebook and start a new translation
        """
        type = w.get_name()
        if type == 'Text':
            translation = TextTranslation (self.application, self.manager)
        else:
            translation = WebTranslation (self.application, self.manager)
                
    def on_settings(self, w):
        """
        FreeSpeak preferences
        """
        Settings(self).start()
                
    def on_about(self, w):
        """
        Open an AboutDialog for this software
        """
        About(self)
                
    def on_delete(self, w, Data=None):
        """
        Put myself in the system tray
        """
        self.tray.wnd_hide()
        return True
            
    def on_quit(self, *w):
        """
        Quit and remove pid file
        """
        try: os.unlink(PID)
        except: pass
        gtk.main_quit()
                
