"""Command-line interface for jobmatcher.

Typical flow:

    # 1. See the ranked shortlist (offline demo needs no keys)
    python -m jobmatcher search --cv data/cv_sample.yaml --offline

    # 2. With live data (needs ADZUNA_APP_ID / ADZUNA_APP_KEY)
    python -m jobmatcher search --cv my_cv.yaml --regions us_h1b,australia

    # 3. Prepare application drafts for the picks you like (1-based indexes)
    python -m jobmatcher apply --cv my_cv.yaml --select 1,3,4 --out out/
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from .config import Config
from .cv import load_cv
from .drafts import write_drafts
from .h1b import H1BSponsorIndex, load_default_index
from .models import Job
from .pipeline import run

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_h1b(args) -> Optional[H1BSponsorIndex]:
    if args.h1b_csv:
        return H1BSponsorIndex.from_csv(args.h1b_csv)
    return load_default_index(_DATA_DIR)


def _shortlist(args) -> List[Job]:
    cv = load_cv(args.cv)
    config = Config.from_env()
    if args.min_score is not None:
        config.min_score = args.min_score
    regions = args.regions.split(",") if args.regions else None
    return run(
        cv,
        config,
        query=args.query,
        regions=regions,
        h1b_index=_load_h1b(args),
        require_h1b_sponsor=args.require_sponsor,
        offline=args.offline,
        top=args.top,
    )


def _print_table(jobs: List[Job]) -> None:
    if not jobs:
        print("No matching jobs found. Try --offline, a broader --query, "
              "or check your Adzuna credentials.")
        return
    print(f"\n{len(jobs)} matches (ranked):\n")
    for i, job in enumerate(jobs, 1):
        spons = ""
        if job.region == "us_h1b":
            spons = " [H1B✓]" if job.sponsors_h1b else " [H1B?]"
        print(f"{i:>2}. {job.match_score:>5.3f}  {job.title} @ {job.company}")
        print(f"      {job.location or job.country.upper()} · {job.region}{spons}")
        if job.matched_terms:
            print(f"      matched: {', '.join(job.matched_terms[:8])}")
        print(f"      {job.url}")
    print()


def cmd_search(args) -> int:
    jobs = _shortlist(args)
    if args.json:
        print(json.dumps([j.to_dict() for j in jobs], indent=2))
    else:
        _print_table(jobs)
    return 0


def cmd_apply(args) -> int:
    jobs = _shortlist(args)
    if not jobs:
        print("Nothing to apply to — the shortlist is empty.")
        return 1

    if args.select:
        idxs = [int(x) for x in args.select.split(",") if x.strip()]
        chosen = [jobs[i - 1] for i in idxs if 1 <= i <= len(jobs)]
    else:
        chosen = jobs

    if not chosen:
        print("No valid selections. Use 1-based indexes from `search`.")
        return 1

    cv = load_cv(args.cv)
    config = Config.from_env()
    folders = write_drafts(cv, chosen, args.out, config)
    print(f"\nWrote {len(folders)} application draft(s) to {args.out}:")
    for folder in folders:
        print(f"  - {folder}")
    print("\nEach folder has a tailored CV, cover letter, a pre-filled form "
          "draft, and APPLY.md.\nNothing was submitted — open each APPLY.md and "
          "submit manually in the portal.\n")
    return 0


def _add_common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--cv", required=True, help="Path to your CV (.yaml/.json)")
    p.add_argument("--query", help="Search query (defaults to your target title)")
    p.add_argument("--regions", help="Comma list: us_h1b,europe_english,"
                   "singapore,australia")
    p.add_argument("--offline", action="store_true",
                   help="Use bundled sample data (no API keys needed)")
    p.add_argument("--h1b-csv", help="Path to a DOL H1B sponsor CSV")
    p.add_argument("--require-sponsor", action="store_true",
                   help="US jobs: keep only employers found in H1B data")
    p.add_argument("--min-score", type=float, help="Minimum match score (0..1)")
    p.add_argument("--top", type=int, default=25, help="Max results")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jobmatcher",
        description="Compliant job-match + CV-tailoring pipeline "
                    "(no scraping, no auto-submit).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    ps = sub.add_parser("search", help="Search and print a ranked shortlist")
    _add_common(ps)
    ps.add_argument("--json", action="store_true", help="Emit JSON")
    ps.set_defaults(func=cmd_search)

    pa = sub.add_parser("apply", help="Write application drafts for selections")
    _add_common(pa)
    pa.add_argument("--select", help="1-based indexes from search, e.g. 1,3,4")
    pa.add_argument("--out", default="out", help="Output directory")
    pa.set_defaults(func=cmd_apply)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
