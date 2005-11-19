"""
    freespeak.py
    Fri Jun 14 13:41:56 2004
    Copyright  2005 Italian Python User Group
    http://www.italianpug.org
   
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

if __name__ == '__main__': 
    import os, sys, os.path, tempfile
    # I use C-c C-c in GNU Emacs, and the argv[0] is blank
    try:
        os.chdir(os.path.dirname(sys.argv[0]))
    except: pass

    from src.nls import Locale
    from src.config import Config

    locale = Locale()
    config = Config()
    locale.use(config.get("interface", "language"))

    from optparse import OptionParser

    parser = OptionParser(usage='%prog [-c] [-q] [ module [ from [ to ] ] ]',
                          version='FreeSpeak 0.1.1') 
    parser.add_option('-c', '--clipboard',
            action='store_true', dest='clipboard', default=False,
            help=_('use clipboard instead of stdin'))
    parser.add_option("-q", "--quiet",
            action="store_false",dest="show_window", default=True,
            help=_("start minimized in tray icon"))
    
    options, args = parser.parse_args()
    PID = os.path.join(tempfile.gettempdir(),
                       'freespeak'+str(os.getuid())+'.pid')
    SOCK = os.path.join(tempfile.gettempdir(),
                        'freespeak'+str(os.getuid())+'.ipc')
    
    import gtk, gtk.gdk
    from src.settings import Settings
    from src.translation import Translation, MiniTranslation
    from src.utils import *
    from src.about import About
    
    class Crash(gtk.Dialog):
        """
        Show non-catched exception in a window
        """
        def __init__(self, *tb):
            gtk.Dialog.__init__(self, 'FreeSpeak - '+_('Crash'), None, 0,
                    (gtk.STOCK_CLOSE, gtk.RESPONSE_OK))
            self.set_keep_above(1)
            self.set_resizable(1)
            self.set_size_request(400, 300)
            
            from traceback import format_exception
            label = gtk.Label()
            label.set_markup('<span color="red"><b>'+
                             _('An error was occurred:')+'</b></span>')
            label.show()
            self.vbox.pack_start(label, 0, 0)
            text = gtk.TextView()
            text.get_buffer().set_text(''.join(format_exception(*tb)))
            scroll = make_text(text)
            scroll.show()
            self.vbox.pack_start(scroll)
            
            self.run()
            try: os.unlink(PID)
            except: pass
    
    sys.excepthook = Crash
    
    import socket
    
    def Start(config, locale):  
        file(PID, 'w').write(str(os.getpid()))
        
        ui_string = """<ui>
        <toolbar>
            <toolitem action="Text" />
            <toolitem action="Web" />
            <toolitem action="Refresh" />
            <toolitem action="Reduce" />
            <toolitem action="Settings" />
            <separator />
            <toolitem action="Quit" />
            <toolitem action="About" />
            <separator />
        </toolbar>
        <accelerator action="Text" />
        <accelerator action="Web" />
        <accelerator action="Refresh" />
        <accelerator action="Reduce" />
        <accelerator action="Settings" />
        <accelerator action="Quit" />
        <accelerator action="About" />
        </ui>"""
                
        class Main(gtk.Window):
            def __init__(self, config, locale):
                gtk.Window.__init__(self)
                self.config = config
                self.locale = locale
                self.clipboard = gtk.Clipboard()
                self.cur_clipboard = ''
                self.is_reduced = 0
                try:
                    self.set_keep_above(self.config.getboolean('translator',
                                                               'alwaysontop'))
                except: pass
                self.load_modules()
                import __builtin__
                __builtin__.error_dialog = self.error
                
                self.set_title('FreeSpeak 0.1.1')
                self.set_border_width(4)
                self.resize(500, 400)
                self.icons = os.path.join(sys.prefix, 'share', 'freespeak',
                                          'icons')
                if(os.path.isfile(os.path.join(self.icons,
                                               "freespeak-16x16.png"))):
                    self.set_icon_from_file(os.path.join(self.icons,
                                                         'freespeak-16x16.png'))
                          
                vbox = gtk.VBox(spacing=6)
                ag = gtk.ActionGroup('WindowActions')
                actions = (
                    ('Text', gtk.STOCK_NEW, _('Text'), "<Control>n",
                     _('New translation'), self.on_new),
                    ('Web', gtk.STOCK_NETWORK, _('Web'), "<Control>e",
                     _('New web page translation'), self.on_new),
                    ('Refresh', gtk.STOCK_REFRESH, _('Refresh'), "<Control>f",
                     _('Refresh module list'), self.on_refresh),
                    ('Reduce', gtk.STOCK_CONVERT, _('Reduce'), "<Control>r",
                     _('Reduce translation window'), self.on_reduce),
                    ('Settings', gtk.STOCK_PREFERENCES, _('Settings'),
                     "<Control>s", _('FreeSpeak settings'), self.on_settings),
                    ('Quit', gtk.STOCK_QUIT, _('Quit'), "<Control>q",
                     _('Quit FreeSpeak'), self.on_quit),
                    ('About', gtk.STOCK_ABOUT, _('About'), "<Control>a",
                     _('About FreeSpeak'), self.on_about),
                )
                ag.add_actions(actions)
                ui = gtk.UIManager()
                ui.insert_action_group(ag, 0)
                ui.add_ui_from_string(ui_string)
                self.accel_group = ui.get_accel_group()
                self.add_accel_group(self.accel_group)
                self.w_toolbar = ui.get_widget("/toolbar")
                self.set_toolbar_style(
                    int(self.config.get("interface", "toolbar")))
                vbox.pack_start(self.w_toolbar, 0)
                self.nb = gtk.Notebook()
                self.nb.set_scrollable(1)
                vbox.pack_start(self.nb)
                self.add(vbox)
                self.tray = None
                try:
                    if self.config.getboolean("miscellaneous", "trayicon"):
                        self.create_trayicon()
                    else:
                        self.h_destroy = self.connect('destroy',
                                                      self.on_quit)  
                except:
                    self.h_destroy = self.connect('destroy',
                                                  self.on_quit) 
                    
                self.reduced = MiniTranslation(self)
                
                # IPC operations
                from Queue import Queue
                import thread
                self.queue = Queue()
                thread.start_new_thread(self.ipc_client, ())
                thread.start_new_thread(self.ipc_server, ())
                
            # Tools
            def set_toolbar_style(self, style):
                if style == 0:
                    self.w_toolbar.unset_style()
                elif style == 1:
                    self.w_toolbar.set_style(gtk.TOOLBAR_BOTH)
                elif style == 2:
                    self.w_toolbar.set_style(gtk.TOOLBAR_ICONS)
                elif style == 3:
                    self.w_toolbar.set_style(gtk.TOOLBAR_TEXT)

            
            def error(self, message, parent=None):
                """
                Run an message dialog for an error
                """
                if not parent: parent = self
                dialog = gtk.MessageDialog(parent,
                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                    gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, message)
                dialog.run()
                dialog.destroy()
                
            def question(self, msg, parent=None):
                """
                Ask a question and return the response of the message dialog
                @param msg: The message to be shown
                @param parent: Specify the transient parent
                @return: Dialog response
                """
                if not parent: parent = self
                dialog = gtk.MessageDialog(parent,
                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                    gtk.MESSAGE_QUESTION, gtk.BUTTONS_NONE, msg)
                dialog.add_buttons(gtk.STOCK_YES, gtk.RESPONSE_YES,
                    gtk.STOCK_NO, gtk.RESPONSE_NO) 
                dialog.set_default_response(gtk.RESPONSE_NO)
                response = dialog.run()
                dialog.destroy()
                return response
        
            def load_modules(self):
                """
                Re-Load translation module list
                """
                self.modules = []
                for module in os.listdir('modules'):
                    if module == '__init__.py' or module[-3:] == 'pyc': continue
                    try:
                        imported_module = reload(getattr(__import__('modules.'+module[:-3]), module[:-3]))
                        
                        imported_module.name
                        translator = imported_module.Translator
                        translator.build_language_table, translator.translate
                        self.modules.append((imported_module.name, translator))
                    except: pass
                
            def make_combo_modules(self, kind="text"):
                """
                Return a combobox with all modules
                """
                combo =  Combo()
                combo_model = gtk.ListStore(str, object)
                for module in self.modules:
                    if kind == "web" and not module[1].web:
                        continue
                    combo_model.append(list(module))
                combo.set_model(combo_model)
                return combo
                
            def preferred_combo_module(self, combo):
                """
                Set the active seletion of the combo to the preferred
                translation module
                """
                preferred_translator = self.config.get("translator",
                                                       "preferred")
                for row in combo.get_model():
                    if row[0] == preferred_translator:
                        combo.set_active_iter(row.iter)
    
            def create_trayicon(self):
                if not self.tray:
                    try:
                        self.disconnect(self.h_destroy)
                    except:
                        pass
                    from src.tray import Trayicon
                    self.tray = Trayicon(self)
                    self.h_delete = self.connect('delete-event', self.on_delete)
    
            def remove_trayicon(self):
                if self.tray:
                    self.disconnect(self.h_delete)
                    self.h_destroy = self.connect('destroy',
                                                  lambda *w:gtk.main_quit()) 
                    self.tray.destroy()
                    self.tray = None
    
                
            def ipc_client(self):
                while 1:
                    try:
                        client = self.queue.get(1)
                        translation = ''
                        while 1:
                            data = client.recv(1)
                            if data == '\x02' or not data:
                                break
                            translation += data
                        translation = filter(lambda x: len(x) > 0,
                                             translation.split('\x01'))

                        be_translated = ''
                        while 1:
                            try:
                                data = client.recv(1)
                                if not data: break
                                be_translated += data
                            except: break
                        if not be_translated:
                            continue

                        def set_combo(combo, data):
                            for row in combo.get_model():
                                if row[0].lower() == data.lower():
                                    gtk.threads_enter()
                                    combo.set_active_iter(row.iter)
                                    gtk.threads_leave()
                                    
                        gtk.threads_enter()
                        self.on_new("Text", False)
                        gtk.threads_leave()
                        translator = self.nb.get_nth_page(
                            self.nb.get_current_page()).page
                        if len(translation) > 0:
                            set_combo(translator.w_module, translation[0])
                            if len(translation) > 1:
                                if translator.translator.language_table:
                                    set_combo(translator.w_from, translation[1])
                                    if len(translation) == 3:
                                        set_combo(translator.w_to,
                                                  translation[2])
                        else:
                            gtk.threads_enter()
                            self.preferred_combo_module(translator.w_module)
                            gtk.threads_leave()
                        translator.w_source.get_buffer().set_text(
                            be_translated)
                        client.close()
                    except: print 'IPC Client Error:', sys.exc_value
                    
            def ipc_server(self):
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                try: os.unlink(SOCK)
                except: pass
                sock.bind(SOCK)
                sock.listen(1)
                while 1:
                    self.queue.put(sock.accept()[0])
            
            # Events
        
            def on_new(self, w, preferred=True):
                """
                Open a new tab in the notebook and start a new translation
                """
                if isinstance(w, str):
                    translation_type = w
                else:
                    translation_type = w.get_name()
                translator = Translation(self, translation_type, preferred)
                self.nb.append_page(translator, translator.tab)
                self.nb.set_current_page(self.nb.get_n_pages()-1)
                
            def on_refresh(self, w):
                """
                Refresh translation module list
                """
                self.load_modules()
                combo = self.make_combo_modules()
                for i in range(self.nb.get_n_pages()):
                    translator = self.nb.get_nth_page(i)
                    w_module = translator.w_module
                    current = w_module.get_active_text()
                    w_module.set_model(combo.get_model())
                    for module in w_module.get_model():
                        if module[0] == current:
                            w_module.set_active_iter(module.iter)
                            break
                    self.preferred_combo_module(w_module)
                
            def on_reduce(self, *w):
                """
                Minimalize the translation window
                """
                self.hide()
                self.reduced.show_all()
                self.is_reduced = 1
                
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
        
        gtk.threads_init()
        sys.excepthook = Crash
        locale.use(config.get("interface", "language"))
        main = Main(config, locale)
        
        if config.getboolean('minimalist', 'startup'):
            main.on_reduce()
        else:
            main.show_all()
        
        if not options.show_window:
            try:
                main.tray.hide()
            except:
                print "I wasn't able to create the tray icon"
        
        gtk.threads_enter()
        gtk.main()
        gtk.threads_leave()
    
    def SubStart():
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(SOCK)
            sock.send('\x01'.join(args[1:4])+'\x02')
            if options.clipboard:
                clipboard = gtk.Clipboard()
                try:
                    if clipboard.wait_is_text_available():
                        be_translated = clipboard.wait_for_text()
                        if not be_translated: raise
                    else: raise
                except:
                    print >> sys.stderr, 'Clipboard contains no text'
                    return
            else:
                be_translated = ''
                while 1:
                    data = raw_input().strip()
                    if data == 'EOF': break
                    be_translated += data
            sock.send(be_translated)
            sock.close()
        except:
            print sys.exc_value
        
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(SOCK)           
        sock.close()
        pid = int(file(PID).read())
        import signal
        os.kill(pid, signal.SIGCHLD)
        SubStart()
    except:
        Start(config, locale)
