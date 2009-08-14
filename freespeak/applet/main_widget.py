#!/usr/bin/env python
import gtk
gtk.gdk.threads_init()

from freespeak import defs
from freespeak import application
import gnomeapplet

class AppHandler (object):
    def __init__ (self):
        self.appinstance = application.get_instance ()

    def start (self):
        self.owned = self.appinstance.start ()

apphandler = AppHandler ()        

class MainWidget (gtk.EventBox):
    def __init__ (self, applet, iid):
        gtk.EventBox.__init__ (self)
        self.applet = applet
        self.iid = iid

        self.set_visible_window (False)
        self.applet.set_background_widget (self.applet)
        self.applet.connect ('change-size', self.on_change_size)

        apphandler.start ()

        self.imagefile = gtk.icon_theme_get_default().lookup_icon("freespeak", 64, 0).get_filename ()
        self.image = gtk.Image ()
        self.image.show ()
        self.add (self.image)
        self.show_all ()

        self.on_change_size (self.applet, self.applet.get_size ())

    def on_change_size (self, applet, size):
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size (self.imagefile, -1, size)
        self.image.set_from_pixbuf (pixbuf)

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
