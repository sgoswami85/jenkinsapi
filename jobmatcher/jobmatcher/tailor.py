"""Tailor a base CV to a specific job.

Two modes:

* Deterministic (default, no network): reorders skills to surface those the job
  mentions, injects a job-targeted headline, and adds a short focus line. This
  is transparent and never fabricates experience.
* LLM-assisted (optional): if an Anthropic API key is configured, rewrites the
  summary to emphasize relevant strengths. It is instructed never to invent
  experience — only to re-emphasize what is already in the CV.
"""

from __future__ import annotations

import copy
from typing import List

from .config import Config
from .models import CV, Job, tokenize


def _job_terms(job: Job) -> set[str]:
    return set(tokenize(f"{job.title} {job.description}"))


def reorder_skills(cv: CV, job: Job) -> List[str]:
    """Put skills the job mentions first, preserving original order within
    each group. Never adds skills the candidate does not have."""
    job_terms = _job_terms(job)
    matched: List[str] = []
    rest: List[str] = []
    for skill in cv.skills:
        skill_tokens = set(tokenize(skill))
        if skill_tokens & job_terms:
            matched.append(skill)
        else:
            rest.append(skill)
    return matched + rest


def tailor_cv(cv: CV, job: Job, config: Config | None = None) -> CV:
    """Return a new CV tailored to the job. Does not mutate the input."""
    config = config or Config()
    tailored = copy.deepcopy(cv)

    tailored.skills = reorder_skills(cv, job)

    # A targeted headline that keeps the candidate's identity but points it at
    # the role. We only borrow the job title, never fake seniority.
    base_headline = cv.headline or (cv.target_titles[0] if cv.target_titles else "")
    if base_headline:
        tailored.headline = f"{base_headline} — targeting {job.title} @ {job.company}"
    else:
        tailored.headline = f"Applicant for {job.title} @ {job.company}"

    focus = _focus_line(cv, job)
    if focus:
        tailored.summary = (cv.summary + "\n\n" + focus).strip() if cv.summary else focus

    if config.has_llm:
        rewritten = _llm_rewrite_summary(cv, job, config)
        if rewritten:
            tailored.summary = rewritten

    return tailored


def _focus_line(cv: CV, job: Job) -> str:
    matched = [s for s in reorder_skills(cv, job)
               if set(tokenize(s)) & _job_terms(job)]
    if not matched:
        return ""
    top = ", ".join(matched[:6])
    return (
        f"Relevant to the {job.title} role at {job.company}: hands-on "
        f"experience with {top}."
    )


def _llm_rewrite_summary(cv: CV, job: Job, config: Config) -> str:
    """Optional Anthropic-powered summary rewrite. Returns "" on any failure so
    the deterministic path remains the fallback."""
    try:
        import anthropic  # type: ignore
    except Exception:
        return ""
    try:
        client = anthropic.Anthropic(api_key=config.anthropic_api_key)
        prompt = (
            "You are tailoring a CV summary to a specific job. Rewrite the "
            "candidate's professional summary to emphasize the strengths most "
            "relevant to the job below. Rules: (1) Do NOT invent experience, "
            "skills, employers, or dates. Only re-emphasize what is present in "
            "the candidate material. (2) Keep it to 3-4 sentences. (3) Return "
            "only the summary text.\n\n"
            f"JOB TITLE: {job.title}\nCOMPANY: {job.company}\n"
            f"JOB DESCRIPTION:\n{job.description}\n\n"
            f"CANDIDATE MATERIAL:\n{cv.searchable_text()}\n\n"
            f"CURRENT SUMMARY:\n{cv.summary}\n"
        )
        msg = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        parts = [b.text for b in msg.content if getattr(b, "type", "") == "text"]
        return "\n".join(parts).strip()
    except Exception:
        return ""
