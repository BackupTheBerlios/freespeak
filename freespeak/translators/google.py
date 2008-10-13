"""
    google.py
    Sun Jun 26 16:42:52 2005
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

import urllib
import lxml.html
#from mechanoid.mechanoid import Browser

from freespeak.translator import BaseTranslator
from freespeak.translation import *

def urlopen(url):
    b = Browser()
    b.addheaders = [ ("User-Agent",
                      "Mozilla/4.7 [en] (X11; U; Linux 2.6.12 i686)")] 
    b.set_handle_robots(0)
    query = b.open(url)
    #b.viewing_html()
    return query.read()

class Language (object):
    def __init__ (self, cc, name):
        self.cc = cc # Country Code
        self.name = name

    def __cmp__ (self, other):
        if self.name < other.name:
            return -1
        elif self.name > other.name:
            return 1
        return 0

    def __str__ (self):
        return self.name

class Translator (BaseTranslator):
    name = 'Google'
    capabilities = [TextTranslationRequest, WebTranslationRequest]
    icon_file = "google-16x16.png"
    
    def __init__(self):
        self.language_table = {}

    def get_language_table(self):
        # Google can handle all language combos
        if self.language_table:
            return self.language_table

        url = 'http://www.google.it/language_tools'
        tree = lxml.html.parse (url)

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

    def set_step(self, step):
        if self.progress:
            gtk.threads_enter()
            self.progress.set_step(step)
            gtk.threads_leave()

    def translate(self, text, kind, progress):
        self.progress = progress

        self.set_step(1)
        abb=""
        for lang in Translator.language_table:
            if lang["from"] == self.from_lang and lang["to"] == self.to_lang:
                abb=lang["abb"]

        source = "text"
        url = "http://translate.google.com/translate_t"

        if kind == "Web":
            source = "u"
            url = "http://translate.google.com/translate_p"
        
        params = urllib.urlencode({source:text, "langpair":abb, "hl":"it", "ie":
                                   "UTF-8", "oe":"UTF-8"})
        url = "%s?%s" % (url, params)

        self.set_step(2)
        try: result = urlopen(url) 
        except:
            gtk.threads_enter()
            error_dialog(_('Error during translation')+'\n\n'+str(sys.exc_value))
            gtk.threads_leave()
            return

        if kind == "Web":
            self.set_step(3)
            url = result[result.index("0;"):]
            url = url[url.index("=")+1:]
            url = url[:url.index('>')-1]
            url = url.replace("&amp;", "&")
            result = urlopen(url)
            return (result, url)

        self.set_step(3)
        result = result[result.index("<textarea"):]
        result = result[:result.index("</textarea")]
        result = re.sub("\<[^<]*\>", "", result).strip()

        self.set_step(4)
        result = result.encode("utf-8")
        
        return result

