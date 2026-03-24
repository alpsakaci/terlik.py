from typing import Optional, List, Dict
from .core import TerlikCore
from .types import TerlikOptions
from .lang import get_language_config, get_supported_languages


class Terlik(TerlikCore):
    """
    Multi-language profanity detection and filtering engine.
    """

    def __init__(self, options: Optional[TerlikOptions] = None):
        opts = options or TerlikOptions()
        lang = opts.language
        lang_config = get_language_config(lang)
        super().__init__(lang_config, opts)

    @staticmethod
    def warmup(
        languages: Optional[List[str]] = None,
        base_options: Optional[TerlikOptions] = None,
    ) -> Dict[str, "Terlik"]:
        langs = languages or get_supported_languages()
        cache: Dict[str, "Terlik"] = {}
        for lang in langs:
            opts = base_options or TerlikOptions()
            opts.language = lang
            instance = Terlik(opts)
            instance.contains_profanity("warmup")
            cache[lang] = instance
        return cache
