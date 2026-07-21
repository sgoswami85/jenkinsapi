"""Base interface for job sources."""

from __future__ import annotations

from typing import List, Protocol

from ..models import Job


class JobSource(Protocol):
    """A job source knows how to fetch postings for a country + query."""

    name: str

    def search(
        self, query: str, country: str, region: str, limit: int
    ) -> List[Job]:
        ...
