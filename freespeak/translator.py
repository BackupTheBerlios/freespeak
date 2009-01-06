# FreeSpeak - a GUI frontend to online translator engines
# freespeak/translator.py
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
Base classes for languages and translator engines
"""

import glob
import os
import imp

from freespeak.translation import (TextTranslationRequest,
                                   WebTranslationRequest,
                                   TranslationSuggestionsRequest)

class BaseLanguage (object):
    """
    Base class for a Language.
    The instance attribute 'cc' is used for the countrycode, if even.
    """

    def is_locale_language (self, cc):
        """
        Checks wheter this language countrycode is the same as the
        given countrycode.
        """
        if hasattr (self, 'cc'):
            return self.cc == cc
        return self == cc

class BaseTranslator (object):
    """
    Base class for Translator.
    A name and a list of capabilities must be set in order to be
    a valid translator.
    """
    name = ""
    capabilities = ()

    def get_name (self):
        """
        Gets the name of the translator
        """
        return self.name

    def translate (self, request):
        """
        Perform the given translation request.
        Override only if you created a new translation request.
        """
        if isinstance (request, TextTranslationRequest):
            return self.translate_text (request)
        elif isinstance (request, WebTranslationRequest):
            return self.translate_web (request)
        elif isinstance (request, TranslationSuggestionsRequest):
            return self.suggest_translations (request)
        else:
            raise RuntimeError (_("Unknown translation request: %s")
                                % str (request))

    def get_language_table (self):
        """
        Virtual method, must be implemented.
        Returns a dictionary of the type { FromLanguage: [ToLanguageOne, ToLanguageTwo, ...] }.
        """
        raise NotImplementedError ()

    def translate_text (self, request):
        """
        Virtual method, must be implemented if text-capable.
        Returns a generator yielding statuses.
        The last object yield must be a StatusTextComplete.
        """
        raise NotImplementedError ()

    def translate_web (self, request):
        """
        Virtual method, must be implemented if web-capable.
        Returns a generator yielding statuses.
        The last object yield must be a StatusWebComplete.
        """
        raise NotImplementedError ()

    def suggest_translations (self, request):
        """
        Virtual method, must be implemented if suggestions-capable.
        Returns a generator yielding statuses.
        The last object yield must be a StatusSuggestionComplete.
        """
        raise NotImplementedError ()

    def __cmp__ (self, other):
        if not other or self.name < other.name:
            return -1
        elif self.name > other.name:
            return 1
        return 0

class TranslatorsManager (set):
    """
    Manages the translator engines in the Python path
    """
    def __init__ (self, application):
        set.__init__ (self)
        self.application = application

        pattern = os.path.join (self.application.translators_path, "*.py")
        files = glob.glob (pattern)
        for fname in files:
            self.load_translator_from_file (fname)

    def load_translator_from_file (self, fname):
        """
        Load the translator given a file name of a valid Python module
        """
        # 1. Split the path and get the latest part of it
        # 2. Split the extension and get the name without .py
        mname = os.path.splitext(os.path.split(fname)[1])[0]
        return self.load_translator (mname)

    def load_translator (self, mname):
        """
        Load the translator given the module name.
        This will look for a Translator class in the module and will
        create an instance of it.
        """
        if mname == '__init__':
            return
        info = imp.find_module (mname, [self.application.translators_path])
        module = imp.load_module (mname, *info)
        if not module in self:
            translator = module.Translator ()
            translator.module_name = mname
            self.add (translator)
            return module

    def get_default (self):
        """
        Returns the default translator according to the configuration
        """
        name = self.application.config.get ("default_translator")
        if name:
            for translator in self:
                if translator.module_name == name:
                    return translator

__all__ = ['BaseLanguage', 'BaseTranslator', 'TranslatorsManager']
