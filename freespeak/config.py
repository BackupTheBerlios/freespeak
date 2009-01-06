# FreeSpeak - a GUI frontend to online translator engines
# freespeak/config.py
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
Configuration manager for FreeSpeak based on GConf
"""

import gconf

class Config (object):
    """
    This class holds a GConf client and wrapper methds around gconf.
    Once an instance is created, the /apps/freespeak dir is added to
    be watched recursively.
    """
    def __init__(self):
        self.client = gconf.client_get_default ()
        self.dir = "/apps/freespeak"
        self.client.add_dir (self.dir, gconf.CLIENT_PRELOAD_RECURSIVE)
        
    def get (self, key):
        """
        Get the value of the given relative key.
        The value is returned as Python object according to the key schema.
        """
        value = self.client.get (self.dir+"/"+key)
        if value.type == gconf.VALUE_STRING:
            return value.get_string ()
        elif value.type == gconf.VALUE_BOOL:
            return value.get_bool ()

    def set (self, key, value):
        """
        Set the given Python object value to the relative key.
        """
        schema = self.client.get_schema ('/schemas'+self.dir+"/"+key)
        gtype = schema.get_type ()
        gvalue = gconf.Value (gtype)
        if gtype == gconf.VALUE_STRING:
            gvalue.set_string (value)
        elif gtype == gconf.VALUE_BOOL:
            gvalue.set_bool (value)
        self.client.set (self.dir+"/"+key, gvalue)
