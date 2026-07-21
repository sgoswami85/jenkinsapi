"""Adzuna job-search API client.

Adzuna publishes a documented, terms-compliant REST API for job search across
many countries including us, gb, nl, de, sg, and au. Get free credentials at
https://developer.adzuna.com/ and set ADZUNA_APP_ID / ADZUNA_APP_KEY.

This is the compliant alternative to scraping LinkedIn.
"""

from __future__ import annotations

from typing import List, Optional
from urllib.parse import urlencode

from ..models import Job

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover - requests is optional at import time
    requests = None

_BASE = "https://api.adzuna.com/v1/api/jobs"


class AdzunaSource:
    name = "adzuna"

    def __init__(self, app_id: str, app_key: str, timeout: int = 20):
        if not app_id or not app_key:
            raise ValueError("Adzuna requires app_id and app_key")
        self.app_id = app_id
        self.app_key = app_key
        self.timeout = timeout

    def search(
        self, query: str, country: str, region: str, limit: int
    ) -> List[Job]:
        if requests is None:
            raise RuntimeError("The 'requests' package is required for Adzuna")

        per_page = min(max(limit, 1), 50)
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "what": query,
            "results_per_page": per_page,
            "content-type": "application/json",
        }
        url = f"{_BASE}/{country}/search/1?" + urlencode(params)
        resp = requests.get(url, timeout=self.timeout)
        resp.raise_for_status()
        payload = resp.json()
        return [
            self._to_job(item, country, region)
            for item in payload.get("results", [])
        ]

    @staticmethod
    def _to_job(item: dict, country: str, region: str) -> Job:
        company = (item.get("company") or {}).get("display_name", "") or ""
        loc = (item.get("location") or {}).get("display_name", "") or ""
        return Job(
            source="adzuna",
            source_id=str(item.get("id", "")),
            title=item.get("title", "") or "",
            company=company,
            location=loc,
            country=country,
            region=region,
            description=item.get("description", "") or "",
            url=item.get("redirect_url", "") or "",
            posted=item.get("created"),
            salary_min=_num(item.get("salary_min")),
            salary_max=_num(item.get("salary_max")),
            currency=_currency_for(country),
            remote="remote" in (item.get("title", "") or "").lower(),
        )


def _num(value) -> Optional[float]:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _currency_for(country: str) -> str:
    return {
        "us": "USD",
        "gb": "GBP",
        "nl": "EUR",
        "de": "EUR",
        "at": "EUR",
        "ch": "CHF",
        "sg": "SGD",
        "au": "AUD",
    }.get(country, "")
