import gtk

class PopupMenu (object):
    def popup (self, event):
        self.menu.popup (None, None, None, event.button, event.time)

class TranslationMenu (PopupMenu):
    ui_string = """<ui>
        <popup>
            <menuitem action="Text" />
            <menuitem action="Web" />
            <menuitem action="Suggestions" />
        </popup>
    </ui>"""

    def __init__ (self, application):
        self.application = application
        actions = (
            ('Text', None, _('_Text'), "",
             _('New translation'), None),

            ('Web', None, _('We_b'), "",
             _('New web page translation'), None),

            ('Suggestions', None, _('_Suggestions'), "",
             _('New translation suggestions'), None))

        self.action_group = gtk.ActionGroup ('TranslationActions')
        self.action_group.add_actions (actions)
        self.ui = gtk.UIManager ()
        self.ui.insert_action_group (self.action_group, 0)
        self.ui.add_ui_from_string (self.ui_string)
        self.menu = self.ui.get_widget ("/popup")

        self.application.configure_actions (self.action_group)
