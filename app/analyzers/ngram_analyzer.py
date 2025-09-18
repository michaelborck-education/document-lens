"""
N-gram analysis utilities (bigrams and trigrams)
"""
import re
from collections import Counter

from app.models.schemas import Ngram


class NgramAnalyzer:
    def __init__(self) -> None:
        pass

    def _tokenize(self, text: str) -> list[str]:
        tokens = re.findall(r"\b[a-zA-Z]+\b", text.lower())
        return tokens

    def extract_ngrams(self, text: str, n: int = 2, top_k: int = 20) -> list[Ngram]:
        tokens = self._tokenize(text)
        if len(tokens) < n:
            return []

        ngrams: Counter[str] = Counter()
        for i in range(len(tokens) - n + 1):
            phrase = " ".join(tokens[i:i+n])
            ngrams[phrase] += 1

        top = ngrams.most_common(top_k)
        return [Ngram(phrase=p, count=c) for p, c in top]
