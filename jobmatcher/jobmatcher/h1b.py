"""H1B sponsorship lookup from public US DOL disclosure data.

The legal, reliable way to tell whether a US employer sponsors H1B visas is the
Department of Labor's public LCA (Labor Condition Application) disclosure data,
published each fiscal year. Load a CSV of employer names (one 'EMPLOYER_NAME'
column, or a single-column list) and this module answers "does company X
sponsor?" via normalized name matching.

Download the source data from:
  https://www.dol.gov/agencies/eta/foreign-labor/performance
"""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Iterable, Optional, Set

_NORMALIZE_RE = re.compile(r"[^a-z0-9 ]+")
_SUFFIXES = {
    "inc", "llc", "ltd", "corp", "corporation", "co", "company",
    "plc", "gmbh", "pte", "pty", "limited", "incorporated", "lp", "llp",
}


def normalize_company(name: str) -> str:
    """Normalize a company name for fuzzy-equality matching."""
    if not name:
        return ""
    lowered = _NORMALIZE_RE.sub(" ", name.lower())
    tokens = [t for t in lowered.split() if t and t not in _SUFFIXES]
    return " ".join(tokens)


class H1BSponsorIndex:
    """Set of normalized employer names known to file LCAs."""

    def __init__(self, names: Optional[Iterable[str]] = None):
        self._names: Set[str] = set()
        for n in names or []:
            norm = normalize_company(n)
            if norm:
                self._names.add(norm)

    def __len__(self) -> int:
        return len(self._names)

    def sponsors(self, company: str) -> bool:
        norm = normalize_company(company)
        if not norm:
            return False
        if norm in self._names:
            return True
        # Prefix/containment fallback: "acme cloud" matches "acme cloud"
        # entries even when the posting adds/drops a trailing word.
        for known in self._names:
            if norm == known:
                return True
            if norm in known or known in norm:
                # Guard against trivial one-token containment noise.
                if min(len(norm), len(known)) >= 4:
                    return True
        return False

    @classmethod
    def from_csv(
        cls, path: str | Path, column: str = "EMPLOYER_NAME"
    ) -> "H1BSponsorIndex":
        path = Path(path)
        names: list[str] = []
        with path.open(newline="", encoding="utf-8", errors="replace") as fh:
            sample = fh.read(4096)
            fh.seek(0)
            has_header = column.lower() in sample.lower()
            if has_header:
                reader = csv.DictReader(fh)
                # Match the column case-insensitively.
                field = next(
                    (f for f in (reader.fieldnames or [])
                     if f and f.lower() == column.lower()),
                    None,
                )
                if field is None:
                    field = (reader.fieldnames or [None])[0]
                for row in reader:
                    if field and row.get(field):
                        names.append(row[field])
            else:
                for row in csv.reader(fh):
                    if row and row[0].strip():
                        names.append(row[0])
        return cls(names)


def load_default_index(data_dir: str | Path) -> H1BSponsorIndex:
    """Load the bundled sample sponsor list; callers should replace it with
    the real DOL export for production use."""
    path = Path(data_dir) / "h1b_sponsors_sample.csv"
    if path.exists():
        return H1BSponsorIndex.from_csv(path)
    return H1BSponsorIndex()
