from .config import config

class TerlikDE:
    def __init__(self, options=None):
        from ...terlik import Terlik
        opts = options or type("Opts", (), {})()
        opts.language = "de"
        self._t = Terlik(opts)
        
    def contains_profanity(self, text):
        return self._t.contains_profanity(text)

    def clean(self, text):
        return self._t.clean(text)

    @property
    def language(self):
        return self._t.language

def create_terlik_de():
    return TerlikDE()
