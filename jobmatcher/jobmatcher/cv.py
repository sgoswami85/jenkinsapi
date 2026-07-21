"""Load and render CVs.

A CV lives as a YAML (or JSON) file so it is easy to hand-edit. This module
loads it into the :class:`~jobmatcher.models.CV` model and renders Markdown.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .models import CV

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - yaml is optional
    yaml = None


def load_cv(path: str | Path) -> CV:
    path = Path(path)
    raw = path.read_text(encoding="utf-8")
    data: Dict[str, Any]
    if path.suffix.lower() in {".yaml", ".yml"}:
        if yaml is None:
            raise RuntimeError(
                "PyYAML is required to read YAML CVs. Install it or use JSON."
            )
        data = yaml.safe_load(raw)
    else:
        data = json.loads(raw)
    return _cv_from_dict(data)


def _cv_from_dict(data: Dict[str, Any]) -> CV:
    known = {f for f in CV.__dataclass_fields__}  # type: ignore[attr-defined]
    filtered = {k: v for k, v in (data or {}).items() if k in known}
    # Required-ish fields with safe defaults.
    filtered.setdefault("name", "")
    filtered.setdefault("headline", "")
    filtered.setdefault("email", "")
    return CV(**filtered)


def render_markdown(cv: CV) -> str:
    """Render a CV to Markdown."""
    lines: list[str] = []
    lines.append(f"# {cv.name}")
    if cv.headline:
        lines.append(f"**{cv.headline}**")
    contact = [x for x in (cv.email, cv.phone, cv.location) if x]
    if cv.links:
        contact.extend(f"{k}: {v}" for k, v in cv.links.items())
    if contact:
        lines.append(" · ".join(contact))
    lines.append("")

    if cv.summary:
        lines.append("## Summary")
        lines.append(cv.summary)
        lines.append("")

    if cv.skills:
        lines.append("## Skills")
        lines.append(", ".join(cv.skills))
        lines.append("")

    if cv.experience:
        lines.append("## Experience")
        for exp in cv.experience:
            title = exp.get("title", "")
            company = exp.get("company", "")
            dates = exp.get("dates", "")
            header = " — ".join(x for x in (title, company) if x)
            if dates:
                header = f"{header} ({dates})" if header else dates
            lines.append(f"### {header}")
            for bullet in exp.get("bullets", []) or []:
                lines.append(f"- {bullet}")
            lines.append("")

    if cv.education:
        lines.append("## Education")
        for edu in cv.education:
            degree = edu.get("degree", "")
            inst = edu.get("institution", "")
            dates = edu.get("dates", "")
            row = " — ".join(x for x in (degree, inst) if x)
            if dates:
                row = f"{row} ({dates})" if row else dates
            lines.append(f"- {row}")
        lines.append("")

    if cv.certifications:
        lines.append("## Certifications")
        for cert in cv.certifications:
            lines.append(f"- {cert}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
