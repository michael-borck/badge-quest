"""Tests for micro-credentials system."""

import pytest

from badgequest.config import CourseConfig
from badgequest.microcredentials import MicroCredentialSystem
from badgequest.models import Database


@pytest.fixture
def test_db(tmp_path):
    """Create a test database."""
    db_path = tmp_path / "test.db"
    return Database(str(db_path))


@pytest.fixture
def test_config():
    """Create a test course configuration with micro-credentials."""
    config_dict = {
        "name": "Test Course",
        "micro_credentials": {
            "ethics_explorer": {
                "name": "Ethics Explorer",
                "emoji": "⚖️",
                "description": "Demonstrated ethical analysis",
                "themes": ["ethics", "responsibility"],
                "min_submissions": 2,
            },
            "innovator": {
                "name": "Innovator",
                "emoji": "💡",
                "description": "Showed creative thinking",
                "themes": ["innovation", "creativity"],
                "min_submissions": 3,
            },
        },
    }
    return CourseConfig("test", config_dict)


def test_no_credentials_without_theme(test_db, test_config):
    """Test that no credentials are awarded without theme."""
    micro_system = MicroCredentialSystem(test_config, test_db)
    
    # No theme provided
    result = micro_system.check_and_award_credentials("student1", "test", None)
    assert result == []
    
    # Empty theme provided
    result = micro_system.check_and_award_credentials("student1", "test", "")
    assert result == []


def test_award_micro_credential(test_db, test_config):
    """Test awarding a micro-credential."""
    micro_system = MicroCredentialSystem(test_config, test_db)
    
    # Add reflections with ethics theme
    test_db.add_reflection(
        student_id="student1",
        course_id="test",
        fingerprint="hash1",
        week_id="week1",
        code="code1",
        word_count=100,
        readability=60.0,
        sentiment=0.5,
        theme_id="ethics",
    )
    
    test_db.add_reflection(
        student_id="student1",
        course_id="test",
        fingerprint="hash2",
        week_id="week2",
        code="code2",
        word_count=150,
        readability=65.0,
        sentiment=0.6,
        theme_id="ethics",
    )
    
    # Check and award credentials
    result = micro_system.check_and_award_credentials("student1", "test", "ethics")
    
    assert len(result) == 1
    assert result[0]["credential_id"] == "ethics_explorer"
    assert result[0]["name"] == "Ethics Explorer"
    assert result[0]["emoji"] == "⚖️"
    assert len(result[0]["weeks_completed"]) == 2


def test_no_duplicate_awards(test_db, test_config):
    """Test that credentials are not awarded twice."""
    micro_system = MicroCredentialSystem(test_config, test_db)
    
    # Add reflections
    test_db.add_reflection(
        student_id="student1",
        course_id="test",
        fingerprint="hash1",
        week_id="week1",
        code="code1",
        word_count=100,
        readability=60.0,
        sentiment=0.5,
        theme_id="ethics",
    )
    
    test_db.add_reflection(
        student_id="student1",
        course_id="test",
        fingerprint="hash2",
        week_id="week2",
        code="code2",
        word_count=150,
        readability=65.0,
        sentiment=0.6,
        theme_id="responsibility",
    )
    
    # First award
    result1 = micro_system.check_and_award_credentials("student1", "test", "ethics")
    assert len(result1) == 1
    
    # Try to award again
    result2 = micro_system.check_and_award_credentials("student1", "test", "ethics")
    assert len(result2) == 0


def test_credentials_progress(test_db, test_config):
    """Test getting progress toward credentials."""
    micro_system = MicroCredentialSystem(test_config, test_db)
    
    # Add one reflection with innovation theme
    test_db.add_reflection(
        student_id="student1",
        course_id="test",
        fingerprint="hash1",
        week_id="week1",
        code="code1",
        word_count=100,
        readability=60.0,
        sentiment=0.5,
        theme_id="innovation",
    )
    
    # Get progress
    progress = micro_system.get_credentials_progress("student1", "test")
    
    # Should have 2 credentials in progress
    assert len(progress) == 2
    
    # Find the innovator credential
    innovator = next(p for p in progress if p["credential_id"] == "innovator")
    assert innovator["status"] == "in_progress"
    assert innovator["progress"] == "1/3"  # 1 out of 3 needed
    assert innovator["weeks_remaining"] == 2