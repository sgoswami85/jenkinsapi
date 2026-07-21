"""Match scoring between a CV and job postings.

A dependency-free TF-IDF + cosine-similarity scorer keeps the pipeline light
and fully offline/deterministic (no sklearn, no network). The corpus is the CV
plus every job description in the current batch, so IDF reflects the batch.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Dict, List, Sequence, Tuple

from .models import CV, Job, tokenize

# Common words we do not want to drive matches.
_STOPWORDS = {
    "the", "and", "for", "with", "you", "our", "are", "will", "have",
    "this", "that", "your", "from", "who", "all", "can", "was", "has",
    "job", "role", "team", "work", "working", "years", "year", "experience",
    "a", "an", "to", "in", "of", "on", "we", "is", "as", "at", "be", "or",
}


def _terms(text: str) -> List[str]:
    return [t for t in tokenize(text) if t not in _STOPWORDS and len(t) > 1]


def _tf(tokens: Sequence[str]) -> Dict[str, float]:
    counts = Counter(tokens)
    total = sum(counts.values()) or 1
    return {term: c / total for term, c in counts.items()}


def _idf(docs: Sequence[Sequence[str]]) -> Dict[str, float]:
    n = len(docs) or 1
    df: Counter = Counter()
    for doc in docs:
        for term in set(doc):
            df[term] += 1
    return {term: math.log((1 + n) / (1 + d)) + 1.0 for term, d in df.items()}


def _vector(tokens: Sequence[str], idf: Dict[str, float]) -> Dict[str, float]:
    tf = _tf(tokens)
    return {term: weight * idf.get(term, 0.0) for term, weight in tf.items()}


def _cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    dot = sum(a[t] * b[t] for t in common)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def score_jobs(cv: CV, jobs: List[Job]) -> List[Job]:
    """Score each job in-place against the CV and return them sorted desc."""
    cv_tokens = _terms(cv.searchable_text())
    job_tokens = [_terms(f"{j.title}\n{j.title}\n{j.description}") for j in jobs]
    # Title is weighted 2x by repetition above.

    idf = _idf([cv_tokens] + job_tokens)
    cv_vec = _vector(cv_tokens, idf)
    cv_term_set = set(cv_tokens)

    for job, tokens in zip(jobs, job_tokens):
        job_vec = _vector(tokens, idf)
        job.match_score = round(_cosine(cv_vec, job_vec), 4)
        overlap = cv_term_set & set(tokens)
        # Rank overlapping terms by their idf weight for a readable summary.
        job.matched_terms = sorted(
            overlap, key=lambda t: idf.get(t, 0.0), reverse=True
        )[:12]

    jobs.sort(key=lambda j: j.match_score, reverse=True)
    return jobs


# --- English-language heuristic for European roles ------------------------

_ENGLISH_SIGNALS = (
    "english", "english-speaking", "fluent english", "english is our",
    "working language is english", "relocation", "visa", "sponsor",
)
_NON_ENGLISH_SIGNALS = (
    "muttersprache", "fließend deutsch", "niederländisch", "nederlands",
    "deutschkenntnisse", "langue française", "sprachkenntnisse",
)


def looks_english(job: Job) -> bool:
    """Cheap heuristic: is this posting likely an English-language role?

    English-native markets (us, gb, au, sg) pass automatically. For continental
    Europe we look for explicit English signals and the absence of strong
    local-language requirements. Not perfect, but keeps obvious mismatches out.
    """
    if job.country in {"us", "gb", "au", "sg", "nz", "ca", "ie"}:
        return True
    text = f"{job.title}\n{job.description}".lower()
    if any(sig in text for sig in _NON_ENGLISH_SIGNALS):
        return False
    # Description itself being in English is a good sign; require at least one
    # explicit English/relocation signal for continental roles.
    return any(sig in text for sig in _ENGLISH_SIGNALS)
