"""
    altavista.py
    Fri Jun 14 13:44:32 2005
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

import urllib, re, sys, gtk

name = 'Altavista'

class Translator:
    web = True
    language_table = []
    icon_file = "altavista-16x16.png"
    
    def __init__(self, parent):
        self.parent = parent
        self.build_language_table()
        self.from_lang="Italian"
        self.to_lang="English"
    
    def build_language_table(self):
        if Translator.language_table: return
        url = 'http://babelfish.altavista.com/tr'
        try:
            query = urllib.urlopen(url)
            result = query.read()
            result = result[result.index("<select name=\"lp\""):]
            result = result[result.index("\n"):result.index("</select>")]
            rows=result.split("\n")
            rows=rows[2:]
        except:
            error_dialog(_('Error during language table loading')+'\n\n'+
                              str(sys.exc_value))
            return
        for row in rows:
            try:
                abb=row[row.index("\"")+1:row.rindex("\"")]
                from_lang=row[row.index(">")+1:row.index(" to")]
                to_lang=row[row.index("to")+3:row.rindex("<")]
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

        if kind == "Web":
            url = "http://babelfish.altavista.com/babelfish/trurl_pagecontent?"
            params = {"lp":abb, "trurl":text} 
        else: 
            url = "http://babelfish.altavista.com/tr?"
            params = {"trtext":text, "lp":abb, "doit":"done", "intl":"1",
                      "tt":"urltext"}
            
        params = urllib.urlencode(params)
        url = "%s%s" % (url, params)

        self.set_step(2)
        try:
            if kind == "Text":
                query = urllib.urlopen(url)
            else:
                opener = urllib.FancyURLopener()
                query = opener.open(url)
        except:
            gtk.threads_enter()
            error_dialog(_('Error during translation')+'\n\n'+
                              str(sys.exc_value))
            gtk.threads_leave()
            return

        self.set_step(3)
        result = query.read()
        if kind == "Text":
            result = result[result.index("<form action=\"http://www.altavista"\
                                         ".com/web/results\""):]
            result = result[result.index("<tr>"):]
            result = result[:result.index("</form>")]
            result = re.sub("\<[^<]*\>", "", result).strip()

            self.set_step(4)
            result = unicode(result, "latin-1")
            result = result.encode("utf-8")
            return result
        return (result, url)
