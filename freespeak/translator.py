import glob
import os
import imp

import freespeak.translators

class TranslatorsManager (list):
    def __init__ (self, application):
        self.application = application

        files = glob.glob (os.path.join (self.application.translators_path, "*.py"))
        for fname in files:
            # 1. Split the path and get the latest part of it
            # 2. Split the extension and get the name without .py
            mname = os.path.splitext(os.path.split(fname)[1])[0]
            if mname == '__init__':
                continue
            info = imp.find_module (mname, [self.application.translators_path])
            print imp.load_module (mname, *info)

