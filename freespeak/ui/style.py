# FreeSpeak - a GUI frontend to online translator engines
# freespeak/ui/style.py
#
## Copyright (C) 2005, 2006, 2007, 2008, 2009  Luca Bruno <lethalman88@gmail.com>
##
## This file is part of FreeSpeak.
##   
## FreeSpeak is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##    
## FreeSpeak is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Library General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA.

"""
Module for modifying the style of GTK+ widgets
"""

import gtk

def setup_rc ():
    """
    Parse an RC style string
    """
    gtk.rc_parse_string ("""
style "tiny-button-style"
{
  GtkWidget::focus-padding = 0
  xthickness = 0
  ythickness = 0
}
widget "*.tiny-button" style "tiny-button-style"

style "intro-button-style"
{
  GtkWidget::focus-padding = 0
  bg[PRELIGHT] = "#fff8ae"
  xthickness = 0
  ythickness = 0
}
widget "*.intro-button" style "intro-button-style"
""")
