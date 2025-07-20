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
        readability = textstat.flesch_reading_ease(text)  # type: ignore

        try:
            blob = TextBlob(text)
            sentiment = float(blob.sentiment.polarity)  # type: ignore
        except Exception:
            # If sentiment analysis fails, default to neutral
            sentiment = 0.0

        # Calculate repetition score
        repetition_score = self._calculate_repetition_score(text)

        return {
            "word_count": word_count, 
            "readability": readability, 
            "sentiment": sentiment,
            "repetition_score": repetition_score
        }
    
    def _calculate_repetition_score(self, text: str) -> float:
        """
        Calculate a repetition score for the text.
        Returns a value between 0 and 1, where higher values indicate more repetition.
        """
        import re
        
        # Split into sentences using multiple delimiters
        sentences = re.split(r'[.!?\n]+', text)
        sentences = [s.strip().lower() for s in sentences if s.strip() and len(s.strip().split()) > 3]
        
        if len(sentences) >= 2:
            # Count unique sentences
            unique_sentences = len(set(sentences))
            total_sentences = len(sentences)
            sentence_repetition = 1.0 - (unique_sentences / total_sentences)
        else:
            sentence_repetition = 0.0
        
        # Check for repeated phrases (3-5 words)
        words = text.lower().split()
        if len(words) < 10:
            return sentence_repetition
        
        # Count phrase repetitions of different lengths
        phrase_scores = []
        
        # Check 3-word, 4-word, and 5-word phrases
        for phrase_len in [3, 4, 5]:
            if len(words) >= phrase_len * 2:  # Need at least 2 phrases
                phrases = []
                for i in range(len(words) - phrase_len + 1):
                    phrase = ' '.join(words[i:i+phrase_len])
                    phrases.append(phrase)
                
                # Count how many times each phrase appears
                phrase_counts = {}
                for phrase in phrases:
                    phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1
                
                # Calculate repetition based on most repeated phrases
                max_repetitions = max(phrase_counts.values()) if phrase_counts else 1
                if max_repetitions > 2:  # Phrase appears 3+ times
                    # Higher weight for longer repeated phrases
                    weight = phrase_len / 5.0
                    phrase_scores.append(min(1.0, (max_repetitions - 1) / 5.0) * weight)
        
        # Get the highest phrase repetition score
        phrase_repetition = max(phrase_scores) if phrase_scores else 0.0
        
        # Combine metrics, giving more weight to phrase repetition
        return max(sentence_repetition, phrase_repetition * 0.8)

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

        # Check for excessive repetition (threshold: 45% repetition)
        if metrics.get("repetition_score", 0) > 0.45:
            return (
                False,
                "Reflection contains too much repetitive content. Please provide more varied and original thoughts.",
                metrics,
            )

        return True, None, metrics
