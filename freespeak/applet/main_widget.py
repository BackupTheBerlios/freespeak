#!/usr/bin/env python
import gtk
gtk.gdk.threads_init()

import sys
from os.path import abspath, join, dirname, exists
import logging
import gettext, locale
import gnomeapplet
from optparse import OptionParser
from freespeak import defs

gettext.install (defs.GETTEXT_PACKAGE, unicode=True)

class MainWidget (gtk.EventBox):
    def __init__ (self, applet, iid):
        gtk.EventBox.__init__ (self)
        self.applet = applet
        self.iid = iid

        but = gtk.Button ("ciao")
        but.show ()
        self.add (but)

def applet_factory (applet, iid):
    widget = MainWidget (applet, iid)
    applet.add (widget)
    applet.show ()
    return True

def bonobo_factory ():
    return gnomeapplet.bonobo_factory (
        "OAFIID:Freespeak_Applet_Factory",
        gnomeapplet.Applet.__gtype__,
        defs.PACKAGE,
        defs.VERSION,
        applet_factory)
