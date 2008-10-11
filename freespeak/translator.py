import glob
import os
import imp

import freespeak.translators

class TranslatorsManager (set):
    def __init__ (self, application):
        set.__init__ (self)
        self.application = application

        files = glob.glob (os.path.join (self.application.translators_path, "*.py"))
        for fname in files:
            self.load_translator_from_file (fname)
            if not module:
                continue

    def load_translator_from_file (self, fname):
        # 1. Split the path and get the latest part of it
        # 2. Split the extension and get the name without .py
        mname = os.path.splitext(os.path.split(fname)[1])[0]
        return self.load_translator (mname)

    def load_translator (self, mname):
        if mname == '__init__':
            return
        info = imp.find_module (mname, [self.application.translators_path])
        module = imp.load_module (mname, *info)
        if not module in self:
            self.add (module)
            return module
