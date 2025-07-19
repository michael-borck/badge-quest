"""Tests for similarity checking."""

from badgequest.similarity import SimilarityChecker


def test_exact_match():
    """Test that identical texts have 100% similarity."""
    checker = SimilarityChecker()
    text = "This is my reflection for this week."
    similarity = checker.calculate_similarity(text, text)
    assert similarity == 1.0


def test_completely_different():
    """Test that completely different texts have low similarity."""
    checker = SimilarityChecker()
    text1 = "This week I learned about machine learning algorithms."
    text2 = "The weather today is sunny and warm outside."
    similarity = checker.calculate_similarity(text1, text2)
    assert similarity < 0.5  # Adjusted - some common words like "the" exist


def test_minor_changes():
    """Test that minor changes are detected as highly similar."""
    checker = SimilarityChecker()
    text1 = "This week I learned about artificial intelligence and its applications."
    text2 = "This week I learned about artificial intelligence and its application."  # removed 's'
    similarity = checker.calculate_similarity(text1, text2)
    assert similarity > 0.95


def test_template_with_changes():
    """Test realistic template use with content changes."""
    checker = SimilarityChecker(threshold=0.8)

    # Week 1 reflection
    text1 = """This week's topic was introduction to AI.
    What I learned: AI is about making machines intelligent.
    What surprised me: The history of AI goes back to the 1950s.
    How I'll apply this: I will look for AI in everyday applications."""

    # Week 2 reflection - same structure, different content
    text2 = """This week's topic was machine learning basics.
    What I learned: ML algorithms learn patterns from data.
    What surprised me: Neural networks mimic the human brain.
    How I'll apply this: I will try to identify ML use cases at work."""

    similarity = checker.calculate_similarity(text1, text2)
    # Should be similar (same structure) but not too similar (different content)
    assert 0.5 < similarity < 0.8  # Allows template use but requires new content


def test_is_too_similar():
    """Test the threshold checking."""
    checker = SimilarityChecker(threshold=0.8)

    text1 = "This is my reflection about AI and machine learning."
    text2 = "This is my reflection about AI and machine learning!"  # Just added punctuation

    assert checker.is_too_similar(text1, text2) is True

    text3 = "My thoughts on deep learning and neural networks today."
    assert checker.is_too_similar(text1, text3) is False


def test_encoding_decoding():
    """Test text encoding and decoding."""
    checker = SimilarityChecker()
    original = "This is my reflection with special characters: é, ñ, 中文"

    encoded = checker.encode_text(original)
    decoded = checker.decode_text(encoded)

    assert decoded == original
    assert encoded != original  # Should be encoded
