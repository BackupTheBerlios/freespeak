# FreeSpeak - a GUI frontend to online translator engines
# freespeak/translation.py - this file is part of FreeSpeak
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

import thread
import gtk

from freespeak.status import *

class TranslationRequest (object):
    def __init__ (self):
        self.from_lang = None
        self.to_lang = None

class TextTranslationRequest (TranslationRequest):
    def __init__ (self, text):
        TranslationRequest.__init__ (self)
        self.text = text

class WebTranslationRequest (TranslationRequest):
    def __init__ (self, url):
        TranslationRequest.__init__ (self)
        self.url = url

class BaseTranslation (object):
    capability = None

    def __init__ (self, application, manager):
        self.application = application
        self.manager = manager
        self.translator = None

        self.setup ()
        self.manager.add_translation (self)
        self.set_default_translator ()

    def close (self):
        self.manager.remove_translation (self)

    def set_default_translator (self):
        default_translator = self.application.translators_manager.get_default ()
        if default_translator:
            self.set_translator (default_translator)

    def set_translator (self, translator):
        self.translator = translator
        if not translator:
            self.update_from_langs (None)
            self.update_to_langs (None)
        else:
            thread.start_new_thread (self._run_language_table, ())
        self.update_translator (translator)

    def set_from_lang (self, lang):
        self.from_lang = lang
        self.update_to_langs (sorted (self.language_table[self.from_lang]))

    def set_to_lang (self, lang):
        self.to_lang = lang
        self.update_can_translate (True)

    def translate (self, request):
        self.update_can_translate (False)
        thread.start_new_thread (self._run, (request,))

    def _run_language_table (self):
        self.update_status (StatusStarted (_("Retrieving languages from %s") % self.translator.get_name ()))
        self.language_table = self.translator.get_language_table (self.capability)
        self.update_status (Status (_("Updating the list")))
        self.update_from_langs (sorted (self.language_table.keys ()))
        self.update_to_langs (None)
        self.update_status (StatusComplete (None))

    def _run (self, request):
        request.from_lang = self.from_lang
        request.to_lang = self.to_lang
        self.update_status (StatusStarted ())
        for status in self.translator.translate (request):
            self.update_status (status)
        self.update_can_translate (True)
        
    # Virtual methods

    def setup (self):
        pass

    def update_translator (self, translator):
        raise NotImplementedError ()

    def update_from_langs (self, langs):
        raise NotImplementedError ()

    def update_to_langs (self, langs):
        raise NotImplementedError ()

    def update_can_translate (self, can_translate):
        raise NotImplementedError ()

    def update_status (self, status, status_text):
        raise NotImplementedError ()

__all__ = ['BaseTranslation', 'TranslationRequest', 'TextTranslationRequest', 'WebTranslationRequest']
