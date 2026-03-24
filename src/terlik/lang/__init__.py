from typing import Dict, List
from .types import LanguageConfig

_configs: Dict[str, LanguageConfig] = {}

def get_language_config(locale: str) -> LanguageConfig:
    if locale in _configs:
        return _configs[locale]
        
    if locale == "tr":
        from .tr.config import config
        _configs["tr"] = config
        return config
    elif locale == "en":
        from .en.config import config
        _configs["en"] = config
        return config
    elif locale == "es":
        from .es.config import config
        _configs["es"] = config
        return config
    elif locale == "de":
        from .de.config import config
        _configs["de"] = config
        return config
        
    raise ValueError(f"Language '{locale}' is not currently supported or not loaded.")

def get_supported_languages() -> List[str]:
    return ["tr", "en", "es", "de"]
