"""Configuration: region -> country mapping, API keys, and loaders."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List

# Logical regions mapped to the country codes used by the Adzuna API.
# English-speaking Europe: UK is the core English-first market; NL/DE/CH/AT/IE
# carry many English-language roles, filtered further by language heuristics.
DEFAULT_REGIONS: Dict[str, List[str]] = {
    "us_h1b": ["us"],
    "europe_english": ["gb", "nl", "de", "ch", "at"],
    "singapore": ["sg"],
    "australia": ["au"],
}

# Country codes supported by the Adzuna API (subset we care about).
ADZUNA_COUNTRIES = {
    "gb", "us", "at", "au", "be", "br", "ca", "ch", "de",
    "es", "fr", "in", "it", "mx", "nl", "nz", "pl", "sg", "za",
}


@dataclass
class Config:
    adzuna_app_id: str = ""
    adzuna_app_key: str = ""
    anthropic_api_key: str = ""
    regions: Dict[str, List[str]] = field(
        default_factory=lambda: dict(DEFAULT_REGIONS)
    )
    results_per_country: int = 25
    # Minimum match score (0..1) to include a job in the shortlist.
    min_score: float = 0.05

    @property
    def has_adzuna(self) -> bool:
        return bool(self.adzuna_app_id and self.adzuna_app_key)

    @property
    def has_llm(self) -> bool:
        return bool(self.anthropic_api_key)

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            adzuna_app_id=os.environ.get("ADZUNA_APP_ID", ""),
            adzuna_app_key=os.environ.get("ADZUNA_APP_KEY", ""),
            anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
        )
