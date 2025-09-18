"""
Advanced text analysis endpoints: n-grams, NER, and contextual keyword search
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.analyzers.keyword_analyzer import KeywordAnalyzer
from app.analyzers.ner_analyzer import NerAnalyzer
from app.analyzers.ngram_analyzer import NgramAnalyzer
from app.models.schemas import KeywordSearchResponse, NERResponse, NgramResponse

router = APIRouter()

# Initialize analyzers
ngram_analyzer = NgramAnalyzer()
ner_analyzer = NerAnalyzer()
keyword_analyzer = KeywordAnalyzer()


class NgramRequest(BaseModel):
    text: str
    n: int = 2
    top_k: int = 20


class NERRequest(BaseModel):
    text: str
    model: str | None = None


class KeywordSearchRequest(BaseModel):
    keyword: str
    documents: list[str]  # list of raw document texts
    document_names: list[str] | None = None


@router.post("/ngrams", response_model=NgramResponse)
async def ngrams(req: NgramRequest) -> NgramResponse:
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    if req.n not in (2, 3):
        raise HTTPException(status_code=400, detail="Only bigrams (2) and trigrams (3) are supported")

    top = ngram_analyzer.extract_ngrams(req.text, n=req.n, top_k=req.top_k)
    return NgramResponse(n=req.n, top_ngrams=top)


@router.post("/ner", response_model=NERResponse)
async def ner(req: NERRequest) -> NERResponse:
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    # If user specified a model and spaCy is available, try to load it
    if req.model and isinstance(ner_analyzer := NerAnalyzer(req.model), NerAnalyzer):
        result = ner_analyzer.analyze(req.text)
        return result

    # Fallback to default analyzer
    result = ner_analyzer.analyze(req.text)
    return result


@router.post("/search/keyword", response_model=KeywordSearchResponse)
async def keyword_search(req: KeywordSearchRequest) -> KeywordSearchResponse:
    if not req.keyword.strip():
        raise HTTPException(status_code=400, detail="Keyword cannot be empty")
    if not req.documents:
        raise HTTPException(status_code=400, detail="Documents cannot be empty")

    names = req.document_names or [f"doc_{i+1}" for i in range(len(req.documents))]
    texts = list(zip(names, req.documents, strict=False))

    return keyword_analyzer.search(texts, req.keyword)
