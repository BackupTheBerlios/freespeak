# FreeSpeak - a GUI frontend to online translator engines
# freespeak/translators/freetranslation.py
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
FreeTranslation engine
"""

import httplib
import urllib
import lxml.html

from freespeak.translator import BaseLanguage, BaseTranslator
from freespeak.translation import (TextTranslationRequest,
                                   WebTranslationRequest)
from freespeak.status import Status, StatusTextComplete, StatusWebComplete

class Language (str, BaseLanguage):
    """
    FreeTranslation haven't countrycode
    """
    pass

class Translator (BaseTranslator):
    """
    FreeTranslation translator
    """
    name = 'FreeTranslation'
    capabilities = [TextTranslationRequest, WebTranslationRequest]
    icon = "freetranslation"
    
    def __init__ (self):
        BaseTranslator.__init__ (self)
        self.text_language_table = {}
        self.web_language_table = {}
    
    def get_language_table (self, capability):
        """
        Overridden. Get the language table depending on the capability.
        """
        if capability == TextTranslationRequest:
            return self._get_language_table (self.text_language_table,
                                             'frmTextTranslator')
        else:
            return self._get_language_table (self.web_language_table,
                                             'frmWebTranslator')

    @staticmethod
    def _get_language_table (language_table, formid):
        """
        FreeTranslation languages are the same, only the html form name changes
        """
        if language_table:
            return language_table

        url = 'http://www.freetranslation.com/'
        tree = lxml.html.parse (urllib.urlopen (url))

        options_path = ('//form[@id="%s"]//select[@name="language"]/option'
                        % formid)
        elements = tree.xpath (options_path)

        for element in elements:
            name_to_name = element.text
            fromlang, tolang = name_to_name.split (' to ')
            
            if not fromlang in language_table:
                language_table[Language (fromlang)] = []
            language_table[Language (fromlang)].append (Language (tolang))

        return language_table

    def translate_text (self, request):
        """
        Issue a POST to / at ets.freetranslation.com
        """
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Accept': 'text/plain'}
        trans = "%s/%s" % (request.from_lang, request.to_lang)
        params = urllib.urlencode ({'sequence': 'core',
                                    'mode': 'text',
                                    'charset': 'UTF-8',
                                    
                                    'language': trans,
                                    'srctext': request.text})

        yield Status (_("Connecting to")+" ets.freetranslation.com")
        conn = httplib.HTTPConnection ('ets.freetranslation.com')
        conn.request ('POST', '/', params, headers)
        result = conn.getresponse().read ()

        yield StatusTextComplete (result)

    def translate_web (self, request):
        """
        Returns a straight url without doing any HTTP request
        """
        trans = "%s/%s" % (request.from_lang, request.to_lang)
        params = urllib.urlencode ({'sequence': 'core',
                                    'language': trans,
                                    'url': request.url})
        yield StatusWebComplete ('http://fets5.freetranslation.com/?'+params)

    def suggest_translations (self, request):
        """
        FreeTranslation doesn't support suggestions
        """
        raise NotImplementedError ()
