"""Validation logic for reflections."""


import textstat
from textblob import TextBlob

from .config import CourseConfig


class ReflectionValidator:
    """Validates reflections against course requirements."""

    def __init__(self, course_config: CourseConfig):
        self.config = course_config

    def analyze_text(self, text: str) -> dict[str, float]:
        """Analyze text and return metrics."""
        word_count = len(text.split())
        readability = textstat.flesch_reading_ease(text)

        try:
            blob = TextBlob(text)
            sentiment = blob.sentiment.polarity
        except Exception:
            # If sentiment analysis fails, default to neutral
            sentiment = 0.0

        return {"word_count": word_count, "readability": readability, "sentiment": sentiment}

    def validate(self, text: str) -> tuple[bool, str | None, dict[str, float]]:
        """
        Validate a reflection against course requirements.

        Returns:
            Tuple of (is_valid, error_message, metrics)
        """
        metrics = self.analyze_text(text)

        if metrics["word_count"] < self.config.min_words:
            return (False, f"Reflection must be at least {self.config.min_words} words", metrics)

        if metrics["readability"] < self.config.min_readability:
            return (
                False,
                f"Reflection readability score must be at least {self.config.min_readability}",
                metrics,
            )

        if metrics["sentiment"] < self.config.min_sentiment:
            return (
                False,
                f"Reflection sentiment must be positive (score > {self.config.min_sentiment})",
                metrics,
            )

        return True, None, metrics
