# FreeSpeak - a GUI frontend to online translator engines
# freespeak/status.py - this file is part of FreeSpeak
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

class Status (object):
    def __init__ (self, description):
        self.description = description

class StatusStarted (Status):
    def __init__ (self, description=None):
        if not description:
            description = _("Translation started")
        Status.__init__ (self, description)

class StatusComplete (Status):
    def __init__ (self, result, description=None):
        if not description:
            description = _("Translation complete")
        Status.__init__ (self, description)
        self.result = result

class StatusTextComplete (StatusComplete):
    pass

class StatusWebComplete (StatusComplete):
    pass

__all__ = ['Status', 'StatusStarted', 'StatusComplete', 'StatusTextComplete', 'StatusWebComplete']
