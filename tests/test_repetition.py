"""Tests for repetition detection in reflections."""

import pytest
from badgequest.config import CourseConfig
from badgequest.validators import ReflectionValidator


def test_repetition_detection():
    """Test that repetitive content is detected and rejected."""
    # Create a test course config
    config = CourseConfig("test", {
        "name": "Test Course",
        "min_words": 50,
        "min_readability": 30,
        "min_sentiment": -1,
    })
    validator = ReflectionValidator(config)
    
    # Test 1: Normal text should pass
    normal_text = """
    Artificial intelligence is transforming how we work and live in profound ways. 
    Machine learning algorithms can now recognize patterns in data that humans might miss. 
    This technology has applications in healthcare, finance, and education sectors worldwide. 
    We need to consider the ethical implications of AI systems carefully and thoughtfully. 
    Privacy and bias are important concerns to address in any AI implementation strategy.
    The future of work will be shaped by how we integrate these technologies responsibly.
    Organizations must balance innovation with responsible deployment of AI systems.
    Training and education will be crucial for workers adapting to these changes.
    """
    is_valid, error, metrics = validator.validate(normal_text)
    assert is_valid
    assert metrics["repetition_score"] < 0.5
    
    # Test 2: Repeated sentences should fail
    repeated_sentences = """
    This is a test sentence about AI. This is a test sentence about AI. 
    This is a test sentence about AI. This is a test sentence about AI.
    This is a test sentence about AI. Machine learning is important.
    This is a test sentence about AI. This is a test sentence about AI.
    """
    is_valid, error, metrics = validator.validate(repeated_sentences)
    assert not is_valid
    assert "repetitive content" in error
    assert metrics["repetition_score"] > 0.5
    
    # Test 3: Repeated phrases should be detected (score is 0.48, above 0.45 threshold)
    repeated_phrases = """
    I think AI is good because AI is good and AI is good for society.
    The reason AI is good is that AI is good for helping people.
    AI is good at solving problems and AI is good at automation.
    We should use AI because AI is good and AI is good for business.
    In conclusion, AI is good and AI is good and AI is good.
    """
    is_valid, error, metrics = validator.validate(repeated_phrases)
    # This text has repetition score around 0.48, so should fail with 0.45 threshold
    assert not is_valid
    assert "repetitive content" in error
    assert metrics["repetition_score"] > 0.45
    
    # Test 4: Slightly varied repetition (trying to game the system)
    varied_repetition = """
    AI is important. AI is very important. AI is really important.
    AI is quite important. AI is extremely important. AI is so important.
    AI is truly important. AI is definitely important. AI is important indeed.
    AI is absolutely important. AI is certainly important. AI is important for sure.
    """
    is_valid, error, metrics = validator.validate(varied_repetition)
    # This should still be caught due to repeated phrase patterns
    assert not is_valid
    assert metrics["repetition_score"] > 0.45


def test_repetition_score_calculation():
    """Test the repetition score calculation directly."""
    config = CourseConfig("test", {"name": "Test", "min_words": 10})
    validator = ReflectionValidator(config)
    
    # Test edge cases
    assert validator._calculate_repetition_score("") == 0.0
    assert validator._calculate_repetition_score("One sentence.") == 0.0
    assert validator._calculate_repetition_score("Short") == 0.0
    
    # Test perfect repetition - short sentences get filtered out
    perfect_repeat = "This is a test sentence. This is a test sentence. This is a test sentence."
    score = validator._calculate_repetition_score(perfect_repeat)
    assert score > 0.6  # Should be high (2/3 sentences are duplicates = 0.667)
    
    # Test no repetition
    no_repeat = "First sentence here. Second one is different. Third is unique too. Fourth has new content."
    score = validator._calculate_repetition_score(no_repeat)
    assert score < 0.3  # Should be low


if __name__ == "__main__":
    pytest.main([__file__, "-v"])