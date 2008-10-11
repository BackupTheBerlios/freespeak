"""
    nls.py
    Mon Aug 01 11:36:56 2005
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

import gettext, os, sys

class Locale:
    def __init__(self):
        self.localedir = os.path.join(sys.prefix, 'freespeak', 'locale')
        self.domain = 'freespeak'
        self.g_translations = {}
        gettext.NullTranslations()
        gettext.install(self.domain, self.localedir)
        try:
            self.g_translations["English"]=gettext.translation(self.domain,
                                                               languages=["en"])
            self.g_translations["Italiano"]=gettext.translation(self.domain,
                                                                languages=['it'])
            self.g_translations["Nederlands"]=gettext.translation(self.domain,
                                                                  languages=['nl'])
        except:
            pass

    def use(self, lang):
        if lang == "System Default":
            import locale
            locale.setlocale(locale.LC_ALL, "")
            try:
                lang=locale.getlocale()[0].split("_")[0]
                gettext.translation(self.domain, languages=[lang]).install()
            except: pass
            return
        try:
            self.g_translations[lang].install()
        except:
            pass

    def get_list(self):
        return self.g_translations.keys()
