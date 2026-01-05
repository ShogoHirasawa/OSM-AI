"""
Settings management for OSM AI Agent plugin.
Handles saving and loading configuration like OpenAI API key.
"""

from typing import Optional
from qgis.PyQt.QtCore import QSettings


SETTINGS_API_KEY = "osm_ai/openai_api_key"
SETTINGS_SEND_SHORTCUT = "osm_ai/send_shortcut"


def save_api_key(api_key: str) -> None:
    """
    Save OpenAI API key to QSettings.
    
    Args:
        api_key: The API key to save (can be empty string)
    """
    settings = QSettings()
    settings.setValue(SETTINGS_API_KEY, api_key)


def load_api_key() -> Optional[str]:
    """
    Load OpenAI API key from QSettings.
    
    Returns:
        The saved API key, or None if not set
    """
    settings = QSettings()
    api_key = settings.value(SETTINGS_API_KEY, None)
    return api_key if api_key else None


def save_send_shortcut(shortcut: str) -> None:
    """
    Save send shortcut preference to QSettings.
    
    Args:
        shortcut: Either "enter" or "cmd_enter"
    """
    settings = QSettings()
    settings.setValue(SETTINGS_SEND_SHORTCUT, shortcut)


def load_send_shortcut() -> str:
    """
    Load send shortcut preference from QSettings.
    
    Returns:
        Either "enter" or "cmd_enter", defaults to "enter"
    """
    settings = QSettings()
    shortcut = settings.value(SETTINGS_SEND_SHORTCUT, "enter")
    return shortcut if shortcut in ["enter", "cmd_enter"] else "enter"

