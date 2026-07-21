"""Prepare application drafts for review — never auto-submit.

For each selected job this writes a self-contained folder containing:
  - tailored_cv.md         : the CV re-emphasized for this role
  - cover_letter.txt       : a factual cover letter
  - application_form.json  : common ATS fields pre-filled from the CV, for you
                             to copy into the real portal
  - APPLY.md               : the apply link + a manual checklist

The application_form.json is a *draft*. Nothing is submitted anywhere; the
apply link opens the employer's own portal where you review and click submit.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

from .config import Config
from .cv import render_markdown
from .coverletter import cover_letter
from .models import CV, Job
from .tailor import tailor_cv


def _slug(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower())
    return text.strip("-")[:60] or "job"


def application_form(cv: CV, job: Job) -> Dict[str, Any]:
    """Common ATS fields pre-filled from the CV. Values you'd paste into most
    Workday/Greenhouse/Lever forms. Draft only — review before use."""
    first, _, last = cv.name.partition(" ")
    return {
        "_note": "DRAFT ONLY — review every field, then submit manually in the portal.",
        "job_title": job.title,
        "company": job.company,
        "job_url": job.url,
        "first_name": first,
        "last_name": last,
        "full_name": cv.name,
        "email": cv.email,
        "phone": cv.phone,
        "location": cv.location,
        "links": cv.links,
        "years_relevant_skills": "",  # you fill in per posting
        "requires_visa_sponsorship": None,  # set true/false yourself
        "authorized_to_work_in_country": None,
        "earliest_start_date": "",
        "salary_expectation": "",
        "how_did_you_hear": "",
    }


def write_draft(
    cv: CV, job: Job, out_dir: str | Path, config: Config | None = None
) -> Path:
    """Write one application-draft folder for a job and return its path."""
    config = config or Config()
    out_dir = Path(out_dir)
    folder = out_dir / f"{_slug(job.company)}__{_slug(job.title)}__{job.source_id or 'x'}"
    folder.mkdir(parents=True, exist_ok=True)

    tailored = tailor_cv(cv, job, config)
    (folder / "tailored_cv.md").write_text(render_markdown(tailored), encoding="utf-8")
    (folder / "cover_letter.txt").write_text(cover_letter(cv, job), encoding="utf-8")
    (folder / "application_form.json").write_text(
        json.dumps(application_form(cv, job), indent=2), encoding="utf-8"
    )

    apply_md = _apply_md(job, tailored)
    (folder / "APPLY.md").write_text(apply_md, encoding="utf-8")
    return folder


def _apply_md(job: Job, tailored: CV) -> str:
    spons = ""
    if job.region == "us_h1b":
        if job.sponsors_h1b is True:
            spons = "- ✅ Employer appears in H1B (DOL LCA) sponsor data.\n"
        elif job.sponsors_h1b is False:
            spons = ("- ⚠️ Employer NOT found in the loaded H1B sponsor data — "
                     "verify sponsorship before applying.\n")
    lines = [
        f"# Apply: {job.title} @ {job.company}",
        "",
        f"- **Location:** {job.location or job.country.upper()}",
        f"- **Region bucket:** {job.region}",
        f"- **Match score:** {job.match_score}",
        f"- **Apply link:** {job.url}",
        spons.rstrip(),
        "",
        "## Manual checklist (nothing is auto-submitted)",
        "1. Open the apply link above.",
        "2. Upload `tailored_cv.md` (export to PDF/DOCX first if required).",
        "3. Paste `cover_letter.txt` where a cover letter is requested.",
        "4. Use `application_form.json` to fill standard fields — review each.",
        "5. Answer sponsorship/work-authorization questions truthfully.",
        "6. Review everything, then click submit yourself.",
        "",
        f"_Top emphasized skills for this role:_ {', '.join(tailored.skills[:8])}",
    ]
    return "\n".join(l for l in lines if l is not None) + "\n"


def write_drafts(
    cv: CV, jobs: List[Job], out_dir: str | Path, config: Config | None = None
) -> List[Path]:
    return [write_draft(cv, job, out_dir, config) for job in jobs]
