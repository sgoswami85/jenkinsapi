"""Core data models shared across the pipeline."""

from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class Job:
    """A single job posting normalized across data sources."""

    source: str
    source_id: str
    title: str
    company: str
    location: str
    country: str  # ISO-ish country code as used by the source, e.g. "us", "gb"
    region: str  # our logical region bucket, e.g. "us_h1b", "europe_english"
    description: str
    url: str
    posted: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: Optional[str] = None
    remote: bool = False
    # Populated by later stages:
    sponsors_h1b: Optional[bool] = None
    match_score: float = 0.0
    matched_terms: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @property
    def short(self) -> str:
        loc = self.location or self.country.upper()
        return f"{self.title} @ {self.company} ({loc})"


@dataclass
class CV:
    """A structured CV. Kept source-format-agnostic so it can be rendered
    to Markdown/plain text and tailored per job."""

    name: str
    headline: str
    email: str
    phone: str = ""
    location: str = ""
    links: Dict[str, str] = field(default_factory=dict)
    summary: str = ""
    skills: List[str] = field(default_factory=list)
    experience: List[Dict[str, Any]] = field(default_factory=list)
    education: List[Dict[str, Any]] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    # Free-form target titles used to bias searches/matching.
    target_titles: List[str] = field(default_factory=list)

    def searchable_text(self) -> str:
        """A single blob used for match scoring."""
        parts: List[str] = [self.headline, self.summary]
        parts.extend(self.skills)
        parts.extend(self.target_titles)
        for exp in self.experience:
            parts.append(str(exp.get("title", "")))
            parts.append(str(exp.get("company", "")))
            bullets = exp.get("bullets", []) or []
            parts.extend(str(b) for b in bullets)
        for edu in self.education:
            parts.append(str(edu.get("degree", "")))
            parts.append(str(edu.get("institution", "")))
        parts.extend(self.certifications)
        return "\n".join(p for p in parts if p)


_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9+#.\-]{1,}")


def tokenize(text: str) -> List[str]:
    """Lowercase word tokenizer that keeps tech tokens like c++, c#, .net."""
    if not text:
        return []
    return [t.lower() for t in _WORD_RE.findall(text)]
