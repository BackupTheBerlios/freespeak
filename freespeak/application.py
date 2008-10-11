"""
FreeSpeak - a simple frontend to already existing online translators
application.py

    Copyright (C) 2005-2006-2007-2008  Luca Bruno <lethalman88@gmail.com>
   
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Library General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
"""

__author__ = "Luca Bruno <lethalman88@gmail.com>"
__version__ = "0.1.1"
__homepage__ = "http://home.gna.org/freespeak"

import gettext
import tempfile
import sys
import os
from optparse import OptionParser

import gtk
from gtk import gdk

from freespeak.config import Config
from freespeak.translator import TranslatorsManager
import freespeak.translators
from freespeak.ui.main_window import MainWindow
from freespeak.ui.exception_dialog import ExceptionDialog
#from freespeak.ipc import IpcServer, IpcClient

class Application (object):
    version = __version__

    def __init__ (self, options={}, args=[]):
        self.domain = 'freespeak'
        self.options = options
        self.args = args

        self.setup_l10n ()
        self.setup_exception_dialog ()
        self.setup_config ()
        self.setup_ipc ()
        self.setup_paths ()
        self.setup_icons ()
        self.setup_translators_manager ()

    def setup_exception_dialog (self):
        sys.excepthook = ExceptionDialog

    def setup_l10n (self):
        gettext.NullTranslations()
        gettext.install(self.domain)

    def setup_config (self):
        self.config = Config ()

    # FIXME:
    def setup_ipc (self):
        self.pid_file = os.path.join(tempfile.gettempdir(), 'freespeak'+str(os.getuid())+'.pid')
        self.sock_file = os.path.join(tempfile.gettempdir(), 'freespeak'+str(os.getuid())+'.sock')

    def setup_paths (self):
        self.icons_path = os.path.join (sys.prefix, 'share', 'freespeak', 'icons')
        self.translators_path = os.path.dirname (freespeak.translators.__file__)

    def setup_icons (self):
        self.icon_factory = gtk.IconFactory ()
        for stock, src in {'freespeak-icon': "freespeak-16x16.png"}.iteritems ():
            file = os.path.join (self.icons_path, src)
            if os.path.isfile (file):
                self.icon_factory.add (stock,
                                       gtk.IconSet (gdk.pixbuf_from_file (file)))
        self.icon_factory.add_default ()

    def setup_translators_manager (self):
        self.translators_manager = TranslatorsManager (self)

    def start (self):
        #client = IpcClient (self)
        #try:
        #    client.execute_start ()
        #    return
        #except:
        #    self.ipc_server = IpcServer (self)

        gtk.gdk.threads_init()
        self.main_window = MainWindow (self)
        self.main_window.show ()

        file(self.pid_file, 'w').write(str (os.getpid()))

        gtk.gdk.threads_enter()
        gtk.main ()
        gtk.gdk.threads_leave()

# FIXME
#     if not options.show_window:
#         try:
#             main.tray.hide()
#         except:
#             print "I wasn't able to create the tray icon"

#     def SubStart():
#         try:
#             sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
#             sock.connect(SOCK)
#             sock.send('\x01'.join(args[1:4])+'\x02')
#             if options.clipboard:
#                 clipboard = gtk.Clipboard()
#                 try:
#                     if clipboard.wait_is_text_available():
#                         be_translated = clipboard.wait_for_text()
#                         if not be_translated: raise
#                     else: raise
#                 except:
#                     print >> sys.stderr, 'Clipboard contains no text'
#                     return
#             else:
#                 be_translated = ''
#                 while 1:
#                     data = raw_input().strip()
#                     if data == 'EOF': break
#                     be_translated += data
#             sock.send(be_translated)
#             sock.close()
#         except:
#             print sys.exc_value
        
#     try:
#         sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
#         sock.connect(SOCK)           
#         sock.close()
#         pid = int(file(PID).read())
#         import signal
#         os.kill(pid, signal.SIGCHLD)
#         SubStart()
#     except:
#         Start(config, locale)
