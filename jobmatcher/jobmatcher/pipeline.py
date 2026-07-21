"""Orchestration: search -> filter -> score -> shortlist -> drafts."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from .config import Config
from .h1b import H1BSponsorIndex
from .matching import looks_english, score_jobs
from .models import CV, Job
from .sources.adzuna import AdzunaSource
from .sources.sample import SampleSource


def build_source(config: Config, offline: bool = False):
    """Pick the compliant live source when credentials exist, else the offline
    sample source."""
    if not offline and config.has_adzuna:
        return AdzunaSource(config.adzuna_app_id, config.adzuna_app_key)
    return SampleSource()


def _default_query(cv: CV) -> str:
    if cv.target_titles:
        return cv.target_titles[0]
    if cv.headline:
        return cv.headline
    return "software engineer"


def search_jobs(
    cv: CV,
    config: Config,
    query: Optional[str] = None,
    regions: Optional[List[str]] = None,
    offline: bool = False,
) -> List[Job]:
    """Fetch postings across the configured regions/countries."""
    source = build_source(config, offline=offline)
    query = query or _default_query(cv)
    regions = regions or list(config.regions.keys())

    jobs: List[Job] = []
    seen: set[tuple[str, str]] = set()
    for region in regions:
        for country in config.regions.get(region, []):
            found = source.search(
                query=query,
                country=country,
                region=region,
                limit=config.results_per_country,
            )
            for job in found:
                key = (job.source, job.source_id)
                if key in seen:
                    continue
                seen.add(key)
                jobs.append(job)
    return jobs


def annotate_and_filter(
    jobs: List[Job],
    h1b_index: Optional[H1BSponsorIndex] = None,
    require_english_europe: bool = True,
    require_h1b_sponsor: bool = False,
) -> List[Job]:
    """Mark H1B sponsorship, apply English-language + sponsorship filters."""
    result: List[Job] = []
    for job in jobs:
        if job.region == "us_h1b" and h1b_index is not None:
            job.sponsors_h1b = h1b_index.sponsors(job.company)
        if job.region == "europe_english" and require_english_europe:
            if not looks_english(job):
                continue
        if (
            job.region == "us_h1b"
            and require_h1b_sponsor
            and job.sponsors_h1b is not True
        ):
            continue
        result.append(job)
    return result


def run(
    cv: CV,
    config: Config,
    *,
    query: Optional[str] = None,
    regions: Optional[List[str]] = None,
    h1b_index: Optional[H1BSponsorIndex] = None,
    require_h1b_sponsor: bool = False,
    require_english_europe: bool = True,
    offline: bool = False,
    top: int = 25,
) -> List[Job]:
    """Full search+filter+score pass, returning the ranked shortlist."""
    jobs = search_jobs(cv, config, query=query, regions=regions, offline=offline)
    jobs = annotate_and_filter(
        jobs,
        h1b_index=h1b_index,
        require_english_europe=require_english_europe,
        require_h1b_sponsor=require_h1b_sponsor,
    )
    jobs = score_jobs(cv, jobs)
    jobs = [j for j in jobs if j.match_score >= config.min_score]
    return jobs[:top]
