# FreeSpeak - a GUI frontend to online translator engines
# freespeak/translators/opentran.py
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
Open-Tran engine
"""

import httplib
import urllib
import lxml.html
import tempfile
import os
import gtk

from freespeak.translator import BaseLanguage, BaseTranslator
from freespeak.translation import TranslationSuggestionsRequest
from freespeak.status import Status, StatusSuggestionsComplete

class Language (BaseLanguage):
    """
    OpenTran languages have countrycode and a name.
    The countrycode is also kept in the name as some languages can't be
    guessed without it.
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

    def __str__ (self):
        return self.name

class Translator (BaseTranslator):
    """
    OpenTran translator
    """
    name = "OpenTran"
    capabilities = [TranslationSuggestionsRequest]
    icon = "opentran"
    pixbuf_cache = {}
    
    def __init__ (self):
        BaseTranslator.__init__ (self)
        self.language_table = {}

    def get_language_table (self, capability):
        """
        Overridden. Get the language table.
        It doesn't depend on the capability as OpenTran can only
        suggest translations.
        """
        # OpenTran can handle all language combos
        if self.language_table:
            return self.language_table

        url = 'http://open-tran.eu/'
        tree = lxml.html.parse (urllib.urlopen (url))

        to_languages = []
        elements = tree.xpath ("//select[@id='form_lang_src']/option")
        for element in elements:
            cc = element.get("value")
            name = element.text
            language = Language (cc, name)
            to_languages.append (language)

        elements = tree.xpath ("//select[@id='form_lang_dst']/option")
        for element in elements:
            cc = element.get("value")
            name = element.text
            language = Language (cc, name)
            self.language_table [language] = to_languages

        return self.language_table
        
    def suggest_translations (self, request):
        """
        Issue a GET to /suggest at open-tran.eu
        """
        params = urllib.urlencode ({'q': request.text,
                                    'src': request.from_lang.cc,
                                    'dst': request.to_lang.cc})

        yield Status (_("Connecting to")+" open-tran.eu")
        conn = httplib.HTTPConnection ('open-tran.eu')
        conn.request ('GET', '/suggest?'+params)
        result = conn.getresponse().read ()

        tree = lxml.html.fromstring (result)
        tree.make_links_absolute ("http://www.open-tran.eu")
        elements = tree.xpath ("//dd/ol/li")
        results = []
        for element in elements:
            yield Status (_("Parsing result"))
            # <a>Word (N&times;<img src="..."></a>
            # <div><a href="...">Application</a>: original</div>
            result = []

            # Translation
            text = element[0].text_content ()
            text = text.rsplit('(', 1)[0].strip ()
            result.append (text)

            # Original text
            text = element[1].text_content().split(':', 1)[1].strip()
            result.append (text)

            # Image
            yield Status (_("Fetching image"))
            image_url = element[0][0].get ("src")
            if image_url in self.pixbuf_cache:
                pixbuf = self.pixbuf_cache[image_url]
            else:
                (fd, filename) = tempfile.mkstemp (suffix="freespeak")
                os.close (fd)
                urllib.urlretrieve (image_url, filename)
                pixbuf = gtk.gdk.pixbuf_new_from_file (filename)
                os.unlink (filename)
                self.pixbuf_cache[image_url] = pixbuf
            result.append (pixbuf)

            # Application
            text = element[1][0].text_content().strip ()
            result.append (text)

            # Project url
            url = element[1][0].get ("href")
            result.append (url)

            results.append (result)

        # Result is a list of suitable lists for ListStore usage
        # [..., (text, original, pixbuf, application, url), ...]
        yield StatusSuggestionComplete (results)

    def translate_text (self, request):
        """
        OpenTran doesn't support text translations
        """
        raise NotImplementedError ()

    def translate_web (self, request):
        """
        OpenTran doesn't support web translations
        """
        raise NotImplementedError ()
