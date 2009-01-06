# FreeSpeak - a GUI frontend to online translator engines
# freespeak/translators/yahoo.py
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
Yahoo Babelfish engine
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
    Yahoo languages have countrycode and a name
    """
    def __init__ (self, cc, name):
        BaseLanguage.__init__ (self)
        self.cc = cc # Country Code
        self.name = name

    def __cmp__ (self, other):
        if not other or self.name < other.name:
            return -1
        elif self.name > other.name:
            return 1
        return 0

    def __eq__ (self, other):
        return self.name == other.name and self.cc == other.cc

    def __hash__ (self):
        return hash (self.cc + self.name)

    def __str__ (self):
        return self.name

class Translator (BaseTranslator):
    """
    Yahoo translator
    """
    name = 'Yahoo!'
    capabilities = [TextTranslationRequest, WebTranslationRequest]
    icon = "yahoo"
    
    def __init__ (self):
        BaseTranslator.__init__ (self)
        self.language_table = {}
    
    def get_language_table (self, capability):
        """
        Overridden. Get the language table.
        It doesn't depend on the capability as Yahoo has equal languages
        for both text and web.
        """
        if self.language_table:
            return self.language_table

        url = 'http://babelfish.yahoo.com/'
        tree = lxml.html.parse (urllib.urlopen (url))

        elements = tree.xpath ('//form[@name="frmTrText"]//select[@name="lp"]/option[@value!=""]')

        for element in elements:
            cc_to_cc = element.get ('value')
            fromcc, tocc = cc_to_cc.split ('_')
            name_to_name = element.text
            fromname, toname = name_to_name.split (' to ')
            fromlang = Language (fromcc, fromname)
            tolang = Language (tocc, toname)
            
            if not fromlang in self.language_table:
                self.language_table[fromlang] = []
            self.language_table[fromlang].append (tolang)

        return self.language_table

    def translate_text (self, request):
        """
        Issue a POST to /translate_txt at babelfish.yahoo.com
        """
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Accept': 'text/plain'}
        lp = request.from_lang.cc+'_'+request.to_lang.cc
        params = urllib.urlencode ({'ei': 'UTF-8',
                                    'doit': 'done',
                                    'fr': 'bf-home',
                                    'intl': '1',
                                    'tt': 'urltext',

                                    'trtext': request.text,
                                    'lp': lp})

        yield Status (_("Connecting to")+" babelfish.yahoo.com")
        conn = httplib.HTTPConnection ('babelfish.yahoo.com')
        conn.request ('POST', '/translate_txt', params, headers)
        result = conn.getresponse().read ()

        yield Status (_("Parsing result"))
        tree = lxml.html.fromstring (result)
        result = tree.get_element_by_id("result").text_content ()

        yield StatusTextComplete (result)

    def translate_web (self, request):
        """
        Returns a straight url without doing any HTTP request
        """
        lp = request.from_lang.cc+'_'+request.to_lang.cc
        params = urllib.urlencode ({'doit': 'done',
                                    'tt': 'url',
                                    'intl': '1',
                                    'fr': 'bf-res',

                                    'lp': lp,
                                    'trurl': request.url})
        url = 'http://babelfish.yahoo.com/translate_url?'+params
        yield StatusWebComplete (url)

    def suggest_translations (self, request):
        """
        Yahoo doesn't support suggestions
        """
        raise NotImplementedError ()
