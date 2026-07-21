"""Generate a straightforward, factual cover letter for a job."""

from __future__ import annotations

from .models import CV, Job, tokenize
from .tailor import reorder_skills


def cover_letter(cv: CV, job: Job) -> str:
    job_terms = set(tokenize(f"{job.title} {job.description}"))
    matched = [s for s in reorder_skills(cv, job)
               if set(tokenize(s)) & job_terms][:5]
    skills_line = (
        f"my experience with {', '.join(matched)}"
        if matched
        else "my background"
    )

    location = job.location or job.country.upper()
    lines = [
        f"Dear Hiring Team at {job.company},",
        "",
        f"I am writing to apply for the {job.title} position ({location}). "
        f"Having reviewed the role, I believe {skills_line} aligns well with "
        f"what your team is looking for.",
        "",
        (cv.summary.split("\n")[0] if cv.summary else
         f"I am a {cv.headline}." if cv.headline else
         "I bring a track record of delivering reliable software."),
        "",
        f"I would welcome the opportunity to discuss how I can contribute to "
        f"{job.company}. Thank you for your consideration.",
        "",
        "Sincerely,",
        cv.name,
    ]
    return "\n".join(lines)
