# FreeSpeak - a GUI frontend to online translator engines
# freespeak/config.py - this file is part of FreeSpeak
#
## Copyright (C) 2005-2008  Luca Bruno <lethalman88@gmail.com>
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
## Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import gconf

class Config (object):
    def __init__(self):
        self.client = gconf.client_get_default ()
        self.dir = "/apps/freespeak/"
        
    def get (self, key):
        value = self.client.get (self.dir+key)
        if value.type == gconf.VALUE_STRING:
            return value.get_string ()
        elif value.type == gconf.VALUE_BOOL:
            return value.get_bool ()

    def set (self, key, value):
        schema = self.client.get_schema ('/schemas'+self.dir+key)
        type = schema.get_type ()
        gvalue = gconf.Value (type)
        if type == gconf.VALUE_STRING:
            gvalue.set_string (value)
        elif type == gconf.VALUE_BOOL:
            gvalue.set_bool (value)
        self.client.set (self.dir+key, gvalue)
