from .config import config

class TerlikES:
    def __init__(self, options=None):
        from ...terlik import Terlik
        opts = options or type("Opts", (), {})()
        opts.language = "es"
        self._t = Terlik(opts)
        
    def contains_profanity(self, text):
        return self._t.contains_profanity(text)

    def clean(self, text):
        return self._t.clean(text)

    @property
    def language(self):
        return self._t.language

def create_terlik_es():
    return TerlikES()
