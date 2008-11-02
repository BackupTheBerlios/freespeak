class Status (object):
    def __init__ (self, description):
        self.description = description

class StatusStarted (Status):
    def __init__ (self, description=None):
        if not description:
            description = _("Translation started")
        Status.__init__ (self, description)

class StatusComplete (Status):
    def __init__ (self, result, description=None):
        if not description:
            description = _("Translation complete")
        Status.__init__ (self, description)
        self.result = result

class StatusTextComplete (StatusComplete):
    pass

class StatusWebComplete (StatusComplete):
    pass

__all__ = ['Status', 'StatusStarted', 'StatusComplete', 'StatusTextComplete', 'StatusWebComplete']
