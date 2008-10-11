"""
    freetranslation.py
    Tue Jul 05 19:06:34 2005
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
name = 'Free Translation'


class Translator:
    web = False
    language_table = []
    icon_file = "freetranslation-16x16.png"
    
    def __init__(self, parent):
        self.parent = parent
        self.build_language_table()
        self.from_lang="English"
        self.to_lang="Russian"
    
    def build_language_table(self):
        if Translator.language_table: return
        url = 'http://www.freetranslation.com/'
        try:
            query = urllib.urlopen(url)
            result = query.read()
            result = result[result.index('<select name="language"'):]
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
                to_lang=row[row.index("to")+3:] #.split()[0]
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

        if "Russian" in self.from_lang:
            text = text.encode("koi8-r")
        elif "Simplified" in self.from_lang:
            text = text.encode("gb2312")
        elif "Traditional" in self.from_lang:
            text = text.encode("big5hkscs")
        else:
            text = text.encode("latin-1")
            
        params = urllib.urlencode({"sequence":"core", "mode":"html",
                                   "template":"results_en-us.htm",
                                   "language":abb,"srctext":text})
        if "Russian" in abb or "Chinese" in abb:
            url = "http://ets6.freetranslation.com/?%s" % params
        else:
            url = "http://ets.freetranslation.com/?%s" % params

        self.set_step(2)
        try:
            query = urllib.urlopen(url)
            result = query.read()
        except:
            gtk.threads_enter()
            error_dialog(_('Error during translation')+'\n\n'+str(sys.exc_value))
            gtk.threads_leave()
            return

        self.set_step(3)
        result = result[result.index("<textarea"):]
        result = result[:result.index("</textarea")]
        result = re.sub("\<[^<]*\>", "", result).strip()

        self.set_step(4)
        if "Russian" in self.to_lang:
            result = unicode(result, "koi8-r")
        elif "Simplified" in self.to_lang:
            result = unicode(result, "gb2312")
        elif "Traditional" in self.to_lang:
            result = unicode(result, "big5hkscs")
        else:
            result = unicode(result, "latin-1")
        result = result.encode("utf-8")

        return result

