"""Text similarity checking for duplicate detection."""

import base64

from Levenshtein import ratio


class SimilarityChecker:
    """Handles text similarity comparisons for reflection submissions."""

    def __init__(self, threshold: float = 0.8):
        """Initialize with similarity threshold (0-1)."""
        self.threshold = threshold

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using Levenshtein ratio.

        Returns:
            float: Similarity score between 0 and 1 (1 = identical)
        """
        # Normalize texts for comparison
        text1_normalized = text1.lower().strip()
        text2_normalized = text2.lower().strip()

        # Use Levenshtein ratio which gives a 0-1 score
        return ratio(text1_normalized, text2_normalized)

    def is_too_similar(self, new_text: str, existing_text: str) -> bool:
        """Check if two texts are too similar based on threshold."""
        similarity = self.calculate_similarity(new_text, existing_text)
        return similarity > self.threshold

    def find_similar_text(
        self, new_text: str, existing_texts: list[str]
    ) -> tuple[bool, float, str]:
        """
        Check if new text is too similar to any existing texts.

        Returns:
            Tuple of (is_similar, max_similarity_score, most_similar_text)
        """
        if not existing_texts:
            return False, 0.0, ""

        max_similarity = 0.0
        most_similar = ""

        for existing_text in existing_texts:
            similarity = self.calculate_similarity(new_text, existing_text)
            if similarity > max_similarity:
                max_similarity = similarity
                most_similar = existing_text

        is_similar = max_similarity > self.threshold
        return is_similar, max_similarity, most_similar

    @staticmethod
    def encode_text(text: str) -> str:
        """Encode text for storage (basic obfuscation, not encryption)."""
        # For MVP, just base64 encode. In production, use proper encryption
        return base64.b64encode(text.encode()).decode()

    @staticmethod
    def decode_text(encoded: str) -> str:
        """Decode stored text."""
        return base64.b64decode(encoded.encode()).decode()
