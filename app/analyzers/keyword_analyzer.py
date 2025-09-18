"""
Contextual keyword search analyzer
"""
import re

from app.models.schemas import KeywordMatch, KeywordSearchResponse

# Helper: ensure type hints for older python/mypy
ListOfText = list[tuple[str, str]]


class KeywordAnalyzer:
    def __init__(self, window: int = 5) -> None:
        self.window = window

    def search(self, texts: list[tuple[str, str]], keyword: str) -> KeywordSearchResponse:
        """
        Search for keyword across multiple documents.

        Args:
            texts: List of tuples (document_name, text)
            keyword: Keyword to search

        Returns:
            KeywordSearchResponse with matches
        """
        keyword_lower = keyword.lower()
        matches: list[KeywordMatch] = []

        for doc_name, text in texts:
            for m in re.finditer(re.escape(keyword_lower), text.lower()):
                start = m.start()
                end = m.end()

                # Compute context window in original text
                words = re.findall(r"\b\w+\b", text)
                # Find word indices surrounding the match by character offsets
                # Map char index to word index approximate
                char_to_word = []
                running = 0
                for _idx, w in enumerate(words):
                    start_char = text.lower().find(w, running)
                    end_char = start_char + len(w)
                    char_to_word.append((start_char, end_char))
                    running = end_char

                # Find the word index containing the match start
                word_idx = 0
                for i, (s_char, e_char) in enumerate(char_to_word):
                    if s_char <= start < e_char:
                        word_idx = i
                        break
                    if i == len(char_to_word)-1:
                        # If not found, approximate
                        word_idx = 0

                left = max(0, word_idx - self.window)
                right = min(len(words), word_idx + self.window + 1)
                context = " ".join(words[left:right])

                matches.append(KeywordMatch(
                    document=doc_name,
                    context=context,
                    start_char=start,
                    end_char=end
                ))

        return KeywordSearchResponse(keyword=keyword, matches=matches)
