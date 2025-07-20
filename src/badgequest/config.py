"""Configuration management for BadgeQuest."""

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load courses from file if specified
def _load_courses_from_env():
    """Load course configurations from environment variable if set."""
    courses_file = os.environ.get("BADGEQUEST_COURSES_FILE")
    if courses_file and Path(courses_file).exists():
        try:
            with open(courses_file) as f:
                import json
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load courses from {courses_file}: {e}")
    return None

# Load external courses if available
_external_courses = _load_courses_from_env()
if _external_courses and "default" not in _external_courses:
    # Always ensure default course exists
    _external_courses["default"] = None  # Will be set to DEFAULT_COURSE later


class BadgeLevel:
    """Represents a badge level configuration."""

    def __init__(self, weeks: int, emoji: str, title: str):
        self.weeks = weeks
        self.emoji = emoji
        self.title = title

    def to_tuple(self) -> tuple[int, str]:
        """Convert to tuple format for backward compatibility."""
        return (self.weeks, f"{self.emoji} {self.title}")


class CourseConfig:
    """Course-specific configuration."""

    def __init__(self, course_id: str, config: dict[str, Any]):
        self.course_id = course_id
        self.name = config.get("name", course_id)
        self.prefix = config.get("prefix", "")
        self.min_words = config.get("min_words", 100)
        self.min_readability = config.get("min_readability", 50)
        self.min_sentiment = config.get("min_sentiment", 0)
        self.max_weeks = config.get("max_weeks", 12)
        self.similarity_threshold = config.get("similarity_threshold", 0.8)

        # Parse badge levels
        self.badge_levels = []
        default_badges = [
            {"weeks": 1, "emoji": "🧪", "title": "Dabbler"},
            {"weeks": 3, "emoji": "🥾", "title": "Explorer"},
            {"weeks": 5, "emoji": "🧠", "title": "Thinker"},
            {"weeks": 7, "emoji": "🛡️", "title": "Warrior"},
            {"weeks": 10, "emoji": "🛠️", "title": "Builder"},
            {"weeks": 12, "emoji": "🗣️", "title": "Explainer"},
            {"weeks": 14, "emoji": "🏆", "title": "Mastery"},
        ]

        badges = config.get("badges", default_badges)
        for badge in badges:
            level = BadgeLevel(
                weeks=badge["weeks"],
                emoji=badge["emoji"],
                title=f"{self.prefix} {badge['title']}" if self.prefix else badge["title"],
            )
            self.badge_levels.append(level)

        # Parse micro-credentials
        self.micro_credentials = {}
        if "micro_credentials" in config:
            self.micro_credentials = config["micro_credentials"]

    def get_badge_tuples(self) -> list[tuple[int, str]]:
        """Get badge levels as tuples for backward compatibility."""
        return [level.to_tuple() for level in self.badge_levels]


class Config:
    """Main configuration class."""

    # Flask configuration
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///reflections.db")

    # CORS configuration
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")

    # Application configuration
    APP_NAME = "BadgeQuest"
    APP_VERSION = "0.3.2"

    # Database configuration
    @property
    def DATABASE_PATH(self) -> str:
        """Extract database path from URL."""
        if self.DATABASE_URL.startswith("sqlite:///"):
            return self.DATABASE_URL.replace("sqlite:///", "")
        return "reflections.db"

    # Default course configuration
    DEFAULT_COURSE = {
        "name": "Default Course",
        "prefix": "",
        "min_words": 100,
        "min_readability": 50,
        "min_sentiment": 0,
        "max_weeks": 12,
        "badges": [
            {"weeks": 1, "emoji": "🧪", "title": "Dabbler"},
            {"weeks": 3, "emoji": "🥾", "title": "Explorer"},
            {"weeks": 5, "emoji": "🧠", "title": "Thinker"},
            {"weeks": 7, "emoji": "🛡️", "title": "Warrior"},
            {"weeks": 10, "emoji": "🛠️", "title": "Builder"},
            {"weeks": 12, "emoji": "🗣️", "title": "Explainer"},
            {"weeks": 14, "emoji": "🏆", "title": "Mastery"},
        ],
    }

    # Course configurations (can be loaded from file or environment)
    # Start with default courses
    _DEFAULT_COURSES = {
        "default": DEFAULT_COURSE,
        "AI101": {
            "name": "Introduction to AI",
            "prefix": "AI",
            "min_words": 100,
            "min_readability": 50,
            "min_sentiment": 0,
            "max_weeks": 12,
            "badges": [
                {"weeks": 1, "emoji": "🧪", "title": "AI Dabbler"},
                {"weeks": 3, "emoji": "🥾", "title": "AI Explorer"},
                {"weeks": 5, "emoji": "🧠", "title": "AI Thinker"},
                {"weeks": 7, "emoji": "🛡️", "title": "AI Warrior"},
                {"weeks": 10, "emoji": "🛠️", "title": "AI Builder"},
                {"weeks": 12, "emoji": "🗣️", "title": "AI Explainer"},
                {"weeks": 14, "emoji": "🏆", "title": "AI Mastery"},
            ],
            "micro_credentials": {
                "ethics_explorer": {
                    "name": "AI Ethics Explorer",
                    "emoji": "⚖️",
                    "description": "Demonstrated strong ethical analysis in AI reflections",
                    "themes": ["ethics", "responsibility"],
                    "min_submissions": 2,
                },
                "innovation_champion": {
                    "name": "Innovation Champion",
                    "emoji": "💡",
                    "description": "Showed creative thinking about AI applications",
                    "themes": ["innovation", "creativity"],
                    "min_submissions": 2,
                },
                "technical_analyst": {
                    "name": "Technical Analyst",
                    "emoji": "🔬",
                    "description": "Demonstrated deep technical understanding",
                    "themes": ["technical", "algorithms"],
                    "min_submissions": 2,
                },
            },
        },
    }

    # Merge external courses with defaults
    COURSES: dict[str, dict[str, Any]] = _DEFAULT_COURSES.copy()
    if _external_courses:
        COURSES.update(_external_courses)
        # Ensure default course always exists
        if "default" not in COURSES:
            COURSES["default"] = DEFAULT_COURSE

    @classmethod
    def get_course_config(cls, course_id: str | None = None) -> CourseConfig:
        """Get configuration for a specific course."""
        if not course_id or course_id not in cls.COURSES:
            course_id = "default"
        return CourseConfig(course_id, cls.COURSES[course_id])

    @classmethod
    def load_from_file(cls, filepath: Path) -> None:
        """Load course configurations from a JSON file."""
        import json

        if filepath.exists():
            with open(filepath) as f:
                courses = json.load(f)
                cls.COURSES.update(courses)
