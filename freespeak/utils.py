# FreeSpeak - a GUI frontend to online translator engines
# freespeak/utils.py
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
Internal utilities for FreeSpeak
"""

import gobject

def syncronized (func):
    """
    Returns a closure to be used as decorator for methods.
    Its purpose is to run the decorated method into the gobject mainloop
    as an idle once a time.
    """
    def closure (*args, **kwargs):
        """
        Add the 'idle' function as a gobject idle
        """
        def idle (*aargs, **kkwargs):
            """
            Call the decorated function and return False to remove the
            gobject idle.
            """
            func (*aargs, **kkwargs)
            return False
        gobject.idle_add (idle, *args, **kwargs)
    return closure
