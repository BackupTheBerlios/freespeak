import gtk

class ScrolledWindow (gtk.ScrolledWindow):
    def __init__ (self, child):
        gtk.ScrolledWindow.__init__ (self)
        self.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.add (child)

def error (message, parent=None):
    """
    Run an message dialog for an error
    """
    dialog = gtk.MessageDialog(parent,
                               gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                               gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, message)
    dialog.run ()
    dialog.destroy()
            
def question(self, message, parent=None):
    """
    Ask a question and return the response of the message dialog
    @param msg: The message to be shown
    @param parent: Specify the transient parent
    @return: Dialog response
    """
    dialog = gtk.MessageDialog(parent,
                               gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                               gtk.MESSAGE_QUESTION, gtk.BUTTONS_NONE, msg)
    dialog.add_buttons(gtk.STOCK_YES, gtk.RESPONSE_YES,
                       gtk.STOCK_NO, gtk.RESPONSE_NO) 
    dialog.set_default_response(gtk.RESPONSE_NO)
    response = dialog.run()
    dialog.destroy()
    return response
