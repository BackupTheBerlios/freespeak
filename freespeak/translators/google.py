# FreeSpeak - a GUI frontend to online translator engines
# freespeak/translators/google.py - this file is part of FreeSpeak
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

import httplib
import urllib
import lxml.html

from freespeak.translator import BaseTranslator
from freespeak.translation import *
from freespeak.status import *

class Language (object):
    def __init__ (self, cc, name):
        self.cc = cc # Country Code
        self.name = name

    def __cmp__ (self, other):
        if not other or self.name < other.name:
            return -1
        elif self.name > other.name:
            return 1
        return 0

    def __eq__ (self, other):
        return self.cc == other.cc and self.name == other.name

    def __str__ (self):
        return self.name

class Translator (BaseTranslator):
    name = 'Google'
    capabilities = [TextTranslationRequest, WebTranslationRequest]
    icon = "google"
    
    def __init__ (self):
        self.language_table = {}

    def get_language_table (self, capability):
        # Google can handle all language combos
        if self.language_table:
            return self.language_table

        url = 'http://www.google.it/language_tools'
        tree = lxml.html.parse (urllib.urlopen (url))

        to_languages = []
        elements = tree.xpath ('//form[@action="http://translate.google.it/translate_t"]//select[@name="tl"]/option')
        for element in elements:
            cc = element.get("value")
            name = element.text
            language = Language (cc, name)
            to_languages.append (language)

        elements = tree.xpath ('//form[@action="http://translate.google.it/translate_t"]//select[@name="sl"]/option')
        for element in elements:
            cc = element.get("value")
            name = element.text
            language = Language (cc, name)
            self.language_table [language] = to_languages

        return self.language_table

    def translate_text (self, request):
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Accept': 'text/plain'}
        params = urllib.urlencode ({'sl': request.from_lang.cc,
                                    'tl': request.to_lang.cc,
                                    'text': request.text})

        yield Status (_("Connecting to")+" translate.google.it")
        conn = httplib.HTTPConnection ('translate.google.it')
        conn.request ('POST', '/translate_t', params, headers)
        result = conn.getresponse().read ()

        yield Status (_("Parsing result"))
        tree = lxml.html.fromstring (result)
        result = tree.get_element_by_id("result_box").text_content()

        yield StatusTextComplete (result)

    def translate_web (self, request):
        params = urllib.urlencode ({'sl': request.from_lang.cc,
                                    'tl': request.to_lang.cc,
                                    'u': request.url})
        yield StatusWebComplete ('http://translate.google.com/translate?'+params)
        
