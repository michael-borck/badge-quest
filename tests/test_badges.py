"""Tests for BadgeQuest badge system."""

from badgequest.badges import BadgeSystem
from badgequest.config import CourseConfig


def test_badge_assignment():
    """Test badge assignment based on weeks completed."""
    config = CourseConfig(
        "test",
        {
            "badges": [
                {"weeks": 1, "emoji": "🌱", "title": "Beginner"},
                {"weeks": 5, "emoji": "🌿", "title": "Intermediate"},
                {"weeks": 10, "emoji": "🌳", "title": "Expert"},
            ]
        },
    )

    badge_system = BadgeSystem(config)

    # Test various week counts
    assert badge_system.assign_badge(0) == "❌ No Badge Yet"
    assert badge_system.assign_badge(1) == "🌱 Beginner"
    assert badge_system.assign_badge(4) == "🌱 Beginner"
    assert badge_system.assign_badge(5) == "🌿 Intermediate"
    assert badge_system.assign_badge(10) == "🌳 Expert"
    assert badge_system.assign_badge(15) == "🌳 Expert"


def test_next_badge_info():
    """Test getting next badge information."""
    config = CourseConfig(
        "test",
        {
            "badges": [
                {"weeks": 1, "emoji": "🌱", "title": "Beginner"},
                {"weeks": 5, "emoji": "🌿", "title": "Intermediate"},
                {"weeks": 10, "emoji": "🌳", "title": "Expert"},
            ]
        },
    )

    badge_system = BadgeSystem(config)

    # Test next badge info
    info = badge_system.get_next_badge_info(0)
    assert info is not None
    assert info["weeks_needed"] == 1
    assert info["next_badge"] == "🌱 Beginner"

    info = badge_system.get_next_badge_info(3)
    assert info is not None
    assert info["weeks_needed"] == 2
    assert info["next_badge"] == "🌿 Intermediate"

    # No next badge for max level
    info = badge_system.get_next_badge_info(15)
    assert info is None
