import gtk

def setup_rc ():
    gtk.rc_parse_string ("""
style "tiny-button-style"
{
  GtkWidget::focus-padding = 0
  xthickness = 0
  ythickness = 0
}
widget "*.tiny-button" style "tiny-button-style"
""")
