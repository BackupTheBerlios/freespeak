# FreeSpeak - a GUI frontend to online translator engines
# freespeak/status.py
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
This module contains a set of classes to describe the status of a translation.
Usually statuses are yield by translators.
"""

class Status (object):
    """
    The base class to describe the most generic translation status
    """

    def __init__ (self, description):
        self.description = description

class StatusStarted (Status):
    """
    Translation has been started.
    Default description is "Translation started".
    """

    def __init__ (self, description=None):
        if not description:
            description = _("Translation started")
        Status.__init__ (self, description)

class StatusComplete (Status):
    """
    Translation has been completed.
    Default description is "Translation complete".
    The object will hold a 'result' attribute set by the translator.
    """

    def __init__ (self, result, description=None):
        if not description:
            description = _("Translation complete")
        Status.__init__ (self, description)
        self.result = result

class StatusCancelled (Status):
    """
    Translation has been cancelled.
    """

    def __init__ (self):
        Status.__init__ (self, _("Cancellation requested"))

class StatusTextComplete (StatusComplete):
    """
    Text translation has been completed.
    """
    pass

class StatusWebComplete (StatusComplete):
    """
    Web page translation has been completed.
    """
    pass

class StatusSuggestionComplete (StatusComplete):
    """
    Translation suggestions has been completed.
    """
    pass

__all__ = ['Status', 'StatusStarted', 'StatusComplete', 'StatusCancelled',
           'StatusTextComplete', 'StatusWebComplete',
           'StatusSuggestionComplete']
