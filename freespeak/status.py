class Status (object):
    def __init__ (self, description):
        self.description

class StatusStarted (object):
    def __init__ (self, description=None):
        if not description:
            description = _("Translation started")
        Status.__init__ (self, description)

class StatusComplete (object):
    def __init__ (self, result, description=None):
        if not description:
            description = _("Translation started")
        Status.__init__ (self, description)
        self.result = result

__all__ = ['Status', 'StatusStarted', 'StatusComplete']
