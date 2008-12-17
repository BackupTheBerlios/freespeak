# FreeSpeak - a GUI frontend to online translator engines
# freespeak/translation.py
#
## Copyright (C) 2005, 2006, 2007, 2008  Luca Bruno <lethalman88@gmail.com>
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

import locale
import threading
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

class TranslationSuggestionsRequest (TranslationRequest):
    def __init__ (self, text):
        TranslationRequest.__init__ (self)
        self.text = text

class Task (threading.Thread):
    def __init__ (self, translation, *args, **kwargs):
        threading.Thread.__init__ (self)
        self.translation = translation
        self.queued_cancel = False

    def cancel (self):
        self.queued_cancel = True

    def run_tasks (self):
        # Must return a generator
        raise NotImplementedError ()

    def run (self):
        for _ in self.run_tasks ():
            if self.queued_cancel:
                return

class TranslatorTask (Task):
    def __init__ (self, translation, translator):
        Task.__init__ (self, translation)
        self.translator = translator

    def run_tasks (self):
        self.translation.update_status (StatusStarted (_("Retrieving languages from %s") % self.translator.get_name ()))
        language_table = self.translator.get_language_table (self.translation.capability)
        yield
        self.translation.language_table = language_table
        self.translation.update_status (Status (_("Updating the list")))
        self.translation.setup_default_language ()
        self.translation.update_from_langs (sorted (self.translation.language_table.keys ()))
        self.translation.update_to_langs (None)
        self.translation.update_can_translate (False)
        self.translation.from_lang = None
        self.translation.to_lang = None
        self.translation.set_default_from_lang ()
        self.translation.update_status (StatusComplete (None))
        self.translation.update_translator (self.translator)
        self.translation.translator = self.translator

class TranslateTask (Task):
    def __init__ (self, translation, request):
        Task.__init__ (self, translation)
        self.request = request

    def run_tasks (self):
        self.request.from_lang = self.translation.from_lang
        self.request.to_lang = self.translation.to_lang
        self.translation.update_status (StatusStarted ())
        for status in self.translation.translator.translate (self.request):
            yield
            self.translation.update_status (status)
        self.translation.update_can_translate (True)

class BaseTranslation (object):
    capability = None

    def __init__ (self, application, manager):
        self.application = application
        self.manager = manager
        self.translator = None
        self.language_table = None
        self.default_lang = None
        self.from_lang = None
        self.to_lang = None
        self.task = None

        self.setup ()
        self.manager.add_translation (self)
        self.set_default_translator ()

    def close (self):
        self.manager.remove_translation (self)

    def set_default_translator (self):
        default_translator = self.application.translators_manager.get_default ()
        if default_translator and self.capability in default_translator.capabilities:
            self.set_translator (default_translator)

    def setup_default_language (self):
        default_locale_language = locale.getdefaultlocale()[0]
        generic_locale_language = default_locale_language.split('_')[0]
        other_default_lang = None
        for language in self.language_table:
            if language.is_locale_language (default_locale_language):
                self.default_lang = language
                return
            elif language.is_locale_language (generic_locale_language):
                other_default_lang = language
        self.default_lang = other_default_lang

    def set_default_from_lang (self):
        if self.default_lang and not self.from_lang and self.to_lang != self.default_lang:
            self.set_from_lang (self.default_lang)

    def set_default_to_lang (self):
        if self.default_lang and not self.to_lang and self.from_lang != self.default_lang:
            self.set_to_lang (self.default_lang)
        elif self.to_lang and self.to_lang in self.language_table[self.from_lang]:
            # Set the previous language if it's still available in the new list
            self.set_to_lang (self.to_lang)
        elif self.default_lang and self.from_lang != self.default_lang:
            # Last chance is to set the default language anyway
            self.set_to_lang (self.default_lang)

    def set_translator (self, translator):
        if not translator:
            self.update_translator (None)
            self.update_from_langs (None)
            self.update_to_langs (None)
            self.update_can_translate (False)
        else:
            self.task = TranslatorTask (self, translator)
            self.task.start ()

    def set_from_lang (self, lang):
        self.from_lang = lang
        self.update_from_lang (self.from_lang)
        self.update_to_langs (sorted (self.language_table[self.from_lang]))
        self.set_default_to_lang ()

    def set_to_lang (self, lang):
        self.to_lang = lang
        self.update_to_lang (self.to_lang)
        self.update_can_translate (True)

    def translate (self, request):
        self.update_can_translate (False)
        self.task = TranslateTask (self, request)
        self.task.start ()
        
    def cancel (self):
        self.task.cancel ()
        self.update_status (StatusCancelled ())
        if isinstance (self.task, TranslateTask):
            self.update_can_translate (True)
        
    # Virtual methods

    def setup (self):
        pass

    def update_translator (self, translator):
        raise NotImplementedError ()

    def update_from_lang (self, lang):
        raise NotImplementedError ()

    def update_to_lang (self, lang):
        raise NotImplementedError ()

    def update_from_langs (self, langs):
        raise NotImplementedError ()

    def update_to_langs (self, langs):
        raise NotImplementedError ()

    def update_can_translate (self, can_translate):
        raise NotImplementedError ()

    def update_status (self, status, status_text):
        raise NotImplementedError ()

__all__ = ['BaseTranslation', 'TranslationRequest',
           'TextTranslationRequest', 'WebTranslationRequest', 'TranslationSuggestionsRequest']
