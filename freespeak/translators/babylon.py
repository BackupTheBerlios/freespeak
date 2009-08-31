# FreeSpeak - a GUI frontend to online translator engines
# freespeak/translators/babylon.py
#
## Copyright (C) 2009  Luca Bruno <lethalman88@gmail.com>
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
Babylon engine
"""

import httplib
import urllib
import lxml.html

from freespeak.translator import BaseLanguage, BaseTranslator
from freespeak.translation import (TextTranslationRequest,
                                   WebTranslationRequest)
from freespeak.status import Status, StatusTextComplete, StatusWebComplete

class Language (BaseLanguage):
    """
    Babylong languages have id and a name
    """
    def __init__ (self, id, name):
        BaseLanguage.__init__ (self)
        self.id = id
        self.name = name

    def is_locale_language (self, cc):
        return False

    def __cmp__ (self, other):
        if not other or self.name < other.name:
            return -1
        elif self.name > other.name:
            return 1
        return 0

    def __eq__ (self, other):
        return self.name == other.name and self.id == other.id

    def __hash__ (self):
        return hash (self.id + self.name)

    def __str__ (self):
        return self.name

class Translator (BaseTranslator):
    """
    Babylon translator
    """
    name = 'Babylon'
    capabilities = [TextTranslationRequest]
    icon = "babylon"
    
    def __init__ (self):
        BaseTranslator.__init__ (self)
        self.language_table = {}
    
    def get_language_table (self, capability):
        """
        Overridden. Get the language table.
        It doesn't depend on the capability as Google can handle all language combos.
        """
        if self.language_table:
            return self.language_table

        url = 'http://translation.babylon.com/'
        tree = lxml.html.parse (urllib.urlopen (url))

        to_languages = []
        elements = tree.xpath ('//select[@name="lpt"]/option')
        for element in elements:
            name = element.text
            if not name.isalnum ():
                continue
            id = element.get ("value")
            language = Language (id, name)
            to_languages.append (language)

        elements = tree.xpath ('//select[@name="lps"]/option')
        for element in elements:
            name = element.text
            if not name.isalnum ():
                continue
            id = element.get ("value")
            language = Language (id, name)
            self.language_table[language] = to_languages

        return self.language_table

    def translate_text (self, request):
        """
        Issue a POST to /translate_txt at babelfish.yahoo.com
        """
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Accept': 'identity'}
        params = urllib.urlencode ({
                'mytextarea1': request.text,
                'lps': request.from_lang.id,
                'lpt': request.to_lang.id})

        yield Status (_("Connecting to")+" translation.babylon.com")
        conn = httplib.HTTPConnection ('translation.babylon.com')
        conn.request ('POST', '/post_post.php', params, headers)
        result = conn.getresponse().read ()

        yield StatusTextComplete (result)
