# FreeSpeak - a GUI frontend to online translator engines
# freespeak/translation.py
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
Base classes for making a Translation and request translations.
"""

import locale
import threading

from freespeak.status import (Status, StatusStarted, StatusComplete,
                              StatusCancelled)

class TranslationRequest (object):
    """
    Base class for translation requests.
    """
    def __init__ (self):
        self.from_lang = None
        self.to_lang = None

class TextTranslationRequest (TranslationRequest):
    """
    Request a translation for the text
    """
    def __init__ (self, text):
        TranslationRequest.__init__ (self)
        self.text = text

class WebTranslationRequest (TranslationRequest):
    """
    Request a translation for the given url
    """
    def __init__ (self, url):
        TranslationRequest.__init__ (self)
        self.url = url

class TranslationSuggestionsRequest (TranslationRequest):
    """
    Request translation suggestions for the given text
    """
    def __init__ (self, text):
        TranslationRequest.__init__ (self)
        self.text = text

class Task (threading.Thread):
    """
    Base class for running a translation task
    """
    def __init__ (self, translation):
        threading.Thread.__init__ (self)
        self.translation = translation
        self.queued_cancel = False

    def cancel (self):
        """
        Queue task cancellation
        """
        self.queued_cancel = True

    def run_tasks (self):
        """
        This is a virtual method that must be implemented to perform the
        real operations.
        It must return a generator.
        """
        raise NotImplementedError ()

    def run (self):
        """
        Externally called. Will run the task and cancel the task when
        requested.
        """
        for _ in self.run_tasks ():
            if self.queued_cancel:
                return

class TranslatorTask (Task):
    """
    A task for running the translator.
    """
    def __init__ (self, translation, translator):
        Task.__init__ (self, translation)
        self.translator = translator

    def run_tasks (self):
        """
        Setup a new translator.
        - Retrieve the language table
        - Setup the default 'from' language
        - Setup the list of 'from' languages
        - Update all the translation parts such as 'translator', 'from', 'to'
        """
        status = StatusStarted (_("Retrieving languages from %s")
                                % self.translator.get_name ())
        self.translation.update_status (status)
        capability = self.translation.capability
        language_table = self.translator.get_language_table (capability)
        yield
        self.translation.language_table = language_table
        self.translation.update_status (Status (_("Updating the list")))
        self.translation.setup_default_language ()
        from_langs = sorted (self.translation.language_table.keys ())
        self.translation.update_from_langs (from_langs)
        self.translation.update_to_langs (None)
        self.translation.update_can_translate (False)
        self.translation.from_lang = None
        self.translation.to_lang = None
        self.translation.set_default_from_lang ()
        self.translation.update_status (StatusComplete (None))
        self.translation.update_translator (self.translator)
        self.translation.translator = self.translator

class TranslateTask (Task):
    """
    A task for doing the translation for real.
    """

    def __init__ (self, translation, request):
        Task.__init__ (self, translation)
        self.request = request

    def run_tasks (self):
        """
        Use the translator to perform the given translation request.
        """
        self.request.from_lang = self.translation.from_lang
        self.request.to_lang = self.translation.to_lang
        self.translation.update_status (StatusStarted ())
        for status in self.translation.translator.translate (self.request):
            yield
            self.translation.update_status (status)
        self.translation.update_can_translate (True)

class BaseTranslation (object):
    """
    The base class for translations.
    Each class must have the capability of satisfying a request (text, web, suggestions).
    """
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
        """
        Remove the translation from the manager
        """
        self.manager.remove_translation (self)

    def set_default_translator (self):
        """
        Set the default translator according to the configuration
        """
        default_translator = self.application.translators_manager.get_default ()
        if (default_translator and
            self.capability in default_translator.capabilities):
            self.set_translator (default_translator)

    def setup_default_language (self):
        """
        Obtain the default system language.
        The result must be the more compatible with online translators.
        """
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
        """
        Set the default 'from' language if it's not been set as 'to' language
        """
        policy = not self.from_lang and self.to_lang != self.default_lang
        if self.default_lang and policy:
            self.set_from_lang (self.default_lang)

    def set_default_to_lang (self):
        """
        Set the default 'to' language if it's not been set as 'from' language
        """
        policy = not self.to_lang and self.from_lang != self.default_lang
        to_langs = self.language_table[self.from_lang]
        if self.default_lang and policy:
            self.set_to_lang (self.default_lang)
        elif self.to_lang and self.to_lang in to_langs:
            # Set the previous language if it's still available in the new list
            self.set_to_lang (self.to_lang)
        elif self.default_lang and self.from_lang != self.default_lang:
            # Last chance is to set the default language anyway
            self.set_to_lang (self.default_lang)

    def set_translator (self, translator):
        """
        Set/unset the translator. This will run the TranslatorTask if necessary.
        """
        if not translator:
            self.update_translator (None)
            self.update_from_langs (None)
            self.update_to_langs (None)
            self.update_can_translate (False)
        else:
            self.task = TranslatorTask (self, translator)
            self.task.start ()

    def set_from_lang (self, lang):
        """
        Set the source language
        """
        self.from_lang = lang
        self.update_from_lang (self.from_lang)
        self.update_to_langs (sorted (self.language_table[self.from_lang]))
        self.set_default_to_lang ()

    def set_to_lang (self, lang):
        """
        Set the destination language.
        """
        self.to_lang = lang
        self.update_to_lang (self.to_lang)
        self.update_can_translate (True)

    def translate (self, request):
        """
        Begin the TranslateTask
        """
        self.update_can_translate (False)
        self.task = TranslateTask (self, request)
        self.task.start ()
        
    def cancel (self):
        """
        Queue cancellation of a running translation
        """
        self.task.cancel ()
        self.update_status (StatusCancelled ())
        if isinstance (self.task, TranslateTask):
            self.update_can_translate (True)
        
    # Virtual methods

    def setup (self):
        """
        Virtual method.
        Setup the translation.
        """
        pass

    def update_translator (self, translator):
        """
        Virtual method, must be implemented.
        Called whenever the translator changes.
        """
        raise NotImplementedError ()

    def update_from_lang (self, lang):
        """
        Virtual method, must be implemented.
        Called whenever the source language changes.
        """
        raise NotImplementedError ()

    def update_to_lang (self, lang):
        """
        Virtual method, must be implemented.
        Called whenever the destination language changes.
        """
        raise NotImplementedError ()

    def update_from_langs (self, langs):
        """
        Virtual method, must be implemented.
        Called whenever the source languages list changes.
        """
        raise NotImplementedError ()

    def update_to_langs (self, langs):
        """
        Virtual method, must be implemented.
        Called whenever the destination languages list changes.
        """
        raise NotImplementedError ()

    def update_can_translate (self, can_translate):
        """
        Virtual method, must be implemented.
        Called whenever a translation request can be satisfied.
        """
        raise NotImplementedError ()

    def update_status (self, status):
        """
        Virtual method, must be implemented.
        Called whenever the status of a translation changes.
        """
        raise NotImplementedError ()

__all__ = ['BaseTranslation', 'TranslationRequest',
           'TextTranslationRequest', 'WebTranslationRequest',
           'TranslationSuggestionsRequest']
