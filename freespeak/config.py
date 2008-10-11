"""
    config.py
    Fri Jun 14 13:41:56 2004
    Copyright (C) 2005-2006-2007-2008  Luca Bruno <lethalman88@gmail.com>
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

from ConfigParser import ConfigParser
import os

class Config(ConfigParser):
    def __init__(self):
        """
        Open existing config file or create one in the user home directory.
        """
        ConfigParser.__init__(self)
        import user
        self.file = user.home+os.sep+'.freespeak'
        try:
            self.readfp(file(self.file))
        except:
            self.add_section('clipboard')
            self.set('clipboard', 'get', 'no')
            self.set('clipboard', 'set', 'no')
            self.add_section("translator")
            self.set("translator", "preferred", "")
            self.add_section("interface")
            self.set("interface", "language", "System Default")
            self.save()
    
    def save(self):
        self.write(file(self.file, 'w'))
        
    def get(self, section, option):
        try: return ConfigParser.get(self, section, option)
        except:
            try: ConfigParser.add_section(self, section)
            except: pass
            self.set(section, option, '')
            return ''
            
    def getboolean(self, section, option):
        try:
            return ConfigParser.getboolean(self, section, option)
        except:
            self.set (section, option, 'no')
            return False
