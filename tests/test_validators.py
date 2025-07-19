"""Tests for reflection validators."""

from badgequest.config import CourseConfig
from badgequest.validators import ReflectionValidator


def test_text_analysis():
    """Test text analysis metrics."""
    config = CourseConfig("test", {"min_words": 100, "min_readability": 50, "min_sentiment": 0})

    validator = ReflectionValidator(config)

    # Test a simple reflection
    text = "This is a test reflection. " * 20  # 100 words
    metrics = validator.analyze_text(text)

    assert metrics["word_count"] == 100
    assert "readability" in metrics
    assert "sentiment" in metrics


def test_validation_word_count():
    """Test word count validation."""
    config = CourseConfig("test", {"min_words": 50, "min_readability": 0, "min_sentiment": -1})

    validator = ReflectionValidator(config)

    # Too short
    is_valid, error, _ = validator.validate("This is too short.")
    assert not is_valid
    assert error is not None and "50 words" in error

    # Just right
    text = "This is a longer reflection. " * 10  # 50 words
    is_valid, error, _ = validator.validate(text)
    assert is_valid
    assert error is None
