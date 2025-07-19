"""BadgeQuest - Collect, learn, repeat.

A gamified reflection system for Learning Management Systems.
"""

__version__ = "0.1.1"
__author__ = "BadgeQuest Contributors"

from .app import create_app
from .badges import BadgeSystem
from .config import Config

__all__ = ["create_app", "BadgeSystem", "Config"]
