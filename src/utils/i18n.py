"""
Internationalization (i18n) Module

Provides translation functions for error messages and user-facing strings.
Supports English and Chinese languages.

Usage:
    from src.utils.i18n import t, set_language, get_language

    # Simple translation
    msg = t("errors.invalid_credentials")

    # Translation with parameters
    msg = t("errors.navigation_failed", url="https://example.com", error="timeout")

    # Change language
    set_language("zh")
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

# Default language
_current_language: str = "en"

# Cache for loaded translations
_translations: Dict[str, Dict[str, Any]] = {}


def _get_config_dir() -> Path:
    """Get the config directory path."""
    # Try to find config relative to project root
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    config_dir = project_root / "config"

    if config_dir.exists():
        return config_dir

    # Fallback: look in test_mcp/config
    test_mcp_config = project_root / "test_mcp" / "config"
    if test_mcp_config.exists():
        return test_mcp_config

    return config_dir


def _load_translations() -> Dict[str, Dict[str, Any]]:
    """Load translations from i18n.json file."""
    global _translations

    if _translations:
        return _translations

    config_dir = _get_config_dir()
    i18n_path = config_dir / "i18n.json"

    if not i18n_path.exists():
        # Return empty translations if file doesn't exist
        return {"en": {"errors": {}}, "zh": {"errors": {}}}

    try:
        with open(i18n_path, encoding="utf-8") as f:
            _translations = json.load(f)
        return _translations
    except (json.JSONDecodeError, IOError):
        return {"en": {"errors": {}}, "zh": {"errors": {}}}


def get_language() -> str:
    """Get the current language."""
    return _current_language


def set_language(lang: str) -> None:
    """Set the current language.

    Args:
        lang: Language code ('en' or 'zh')
    """
    global _current_language
    if lang in ("en", "zh"):
        _current_language = lang
    else:
        # Default to English for unknown languages
        _current_language = "en"


def set_language_from_env() -> None:
    """Set language from SHADOW_LANGUAGE environment variable."""
    lang = os.environ.get("SHADOW_LANGUAGE", "").strip().lower()
    if lang in ("en", "zh"):
        set_language(lang)


def _get_nested_value(data: Dict[str, Any], key_path: str) -> Optional[str]:
    """Get a nested value from a dictionary using dot notation.

    Args:
        data: Dictionary to search
        key_path: Dot-separated key path (e.g., "errors.invalid_credentials")

    Returns:
        The value if found, None otherwise
    """
    keys = key_path.split(".")
    current = data

    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None

    return current if isinstance(current, str) else None


def t(key: str, **kwargs: Any) -> str:
    """
    Translate a key to the current language.

    Args:
        key: Translation key in dot notation (e.g., "errors.invalid_credentials")
        **kwargs: Format parameters for the translation string

    Returns:
        Translated string with parameters substituted

    Example:
        t("errors.navigation_failed", url="https://example.com", error="timeout")
        # Returns: "Navigation failed for https://example.com: timeout"
    """
    translations = _load_translations()
    lang_data = translations.get(_current_language, translations.get("en", {}))

    # Try to get the translation
    value = _get_nested_value(lang_data, key)

    # Fallback to English if not found in current language
    if value is None and _current_language != "en":
        en_data = translations.get("en", {})
        value = _get_nested_value(en_data, key)

    # Return key if translation not found
    if value is None:
        return key

    # Format with kwargs if provided
    if kwargs:
        try:
            return value.format(**kwargs)
        except (KeyError, ValueError):
            # If formatting fails, return the original string
            return value

    return value


def tr(key: str, lang: Optional[str] = None, **kwargs: Any) -> str:
    """
    Translate a key to a specific language.

    Args:
        key: Translation key
        lang: Language code ('en' or 'zh'), uses current language if None
        **kwargs: Format parameters

    Returns:
        Translated string
    """
    original_lang = _current_language
    if lang:
        set_language(lang)

    result = t(key, **kwargs)

    if lang:
        set_language(original_lang)

    return result


def get_available_languages() -> list:
    """Get list of available language codes."""
    translations = _load_translations()
    return list(translations.keys())


def reload_translations() -> None:
    """Clear cache and reload translations from file."""
    global _translations
    _translations = {}
    _load_translations()


# Initialize language from environment on module import
set_language_from_env()
