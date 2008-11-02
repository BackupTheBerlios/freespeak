import gtk

class StatusIcon (gtk.StatusIcon):
    def __init__ (self, window):
        gtk.StatusIcon.__init__ (self)
        self.window = window

        self.set_from_stock (gtk.STOCK_NETWORK)

        self.connect ('activate', self.on_activate)
        self.connect ('popup-menu', self.on_popup_menu)

    def on_activate (self, *args):
        if self.window.is_active ():
            self.tray ()
        else:
            self.untray ()

    def on_popup_menu (self, status_icon, button, activate_time):
        menu = gtk.Menu ()
        menu.set_accel_group (self.window.accel_group)
        item = self.window.action_group.get_action("Preferences").create_menu_item ()
        menu.append (item)
        item = self.window.action_group.get_action("About").create_menu_item ()
        menu.append (item)
        item = gtk.SeparatorMenuItem ()
        item.show ()
        menu.append (item)
        item = self.window.action_group.get_action("Quit").create_menu_item ()
        menu.append (item)
        menu.popup (None, None, gtk.status_icon_position_menu,
                    button, activate_time, status_icon)
        
    def tray (self):
        self.window.set_skip_taskbar_hint (True)
        self.window.iconify ()

    def untray (self):
        self.window.present ()
        self.window.set_skip_taskbar_hint (False)
