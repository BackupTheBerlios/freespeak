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

import re, sys, gtk, urllib
#from mechanoid.mechanoid import Browser

from freespeak.translator import BaseTranslator

def urlopen(url):
    b = Browser()
    b.addheaders = [ ("User-Agent",
                      "Mozilla/4.7 [en] (X11; U; Linux 2.6.12 i686)")] 
    b.set_handle_robots(0)
    query = b.open(url)
    #b.viewing_html()
    return query.read()
    
class Translator (BaseTranslator):
    name = 'Google'
    web = True
    language_table = []
    icon_file = "google-16x16.png"
    
    def __init__(self):
        self.from_lang="Italian"
        self.to_lang="English"
    
    def build_language_table(self):
        if Translator.language_table: return
        url = 'http://translate.google.com/translate_t'
        try: 
            result = urlopen(url)
            result = result[result.index("<select name=langpair>"):]
            result = result[result.index("<option"):]
            result = result[:result.index("</select>")]
            result = result.replace("&", " ")
            rows=result.split("</option>")
            rows=rows[2:]
        except:
            error_dialog(_('Error during language table loading')+
                              '\n\n'+str(sys.exc_value)) 
            return
        for row in rows:
            try:
                abb=row[row.index("\"")+1:row.rindex("\"")]
                from_lang=row[row.index(">")+1:row.index(" to")].split()[0]
                to_lang=row[row.index("to")+3:].split()[0]
                Translator.language_table.append({"from":from_lang,
                                                  "to":to_lang, "abb":abb})
            except:
                pass

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

