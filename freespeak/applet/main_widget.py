#!/usr/bin/env python
import gtk
gtk.gdk.threads_init()

from freespeak import defs
from freespeak import application
import menus
import gnomeapplet

class AppHandler (object):
    def __init__ (self):
        self.appinstance = application.get_instance ()

    def start (self):
        self.owned = self.appinstance.start (show_main_window=False)

class MainWidget (gtk.EventBox):
    """
    The main applet widget displaying the icon in the panel and listening for
    mouse events. 
    It will display translations menu if left-clicked, while preferences and
    other information when right-clicked.
    """

    def __init__ (self, applet, iid):
        gtk.EventBox.__init__ (self)
        self.applet = applet
        self.iid = iid
        self.connect ('button-press-event', self.on_button_press_event)

        self.apphandler = AppHandler ()
        self.apphandler.start ()
        self.translation_menu = menus.TranslationMenu (self.apphandler.appinstance)

        self.set_visible_window (False)
        self.applet.set_background_widget (self.applet)
        self.applet.connect ('change-size', self.on_change_size)

        self.imagefile = gtk.icon_theme_get_default().lookup_icon("freespeak", 64, 0).get_filename ()
        self.image = gtk.Image ()
        self.image.show ()
        self.add (self.image)
        self.show_all ()

        self.on_change_size (self.applet, self.applet.get_size ())

    def on_button_press_event (self, widget, event):
        if event.button == 1:
            self.translation_menu.popup (event)
        elif event.button == 3:
            self.popup_application_menu (event)

    def on_change_size (self, applet, size):
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size (self.imagefile, -1, size)
        self.image.set_from_pixbuf (pixbuf)

    def popup_application_menu (self, event):
        pass

def applet_factory (applet, iid):
    widget = MainWidget (applet, iid)
    applet.add (widget)
    applet.show_all ()
    return True

def bonobo_factory ():
    return gnomeapplet.bonobo_factory (
        "OAFIID:Freespeak_Applet_Factory",
        gnomeapplet.Applet.__gtype__,
        defs.PACKAGE,
        defs.VERSION,
        applet_factory)
