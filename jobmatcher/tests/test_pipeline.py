import json

from jobmatcher.config import Config
from jobmatcher.cv import load_cv
from jobmatcher.h1b import load_default_index
from jobmatcher.drafts import write_drafts
from jobmatcher.pipeline import run
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"


def test_offline_run_returns_ranked_shortlist():
    cv = load_cv(DATA / "cv_sample.yaml")
    config = Config()
    h1b = load_default_index(DATA)
    jobs = run(cv, config, h1b_index=h1b, offline=True, top=25)
    assert jobs, "expected at least one match from sample data"
    scores = [j.match_score for j in jobs]
    assert scores == sorted(scores, reverse=True)
    # US sample employers should be annotated for H1B.
    us = [j for j in jobs if j.region == "us_h1b"]
    assert any(j.sponsors_h1b is True for j in us)


def test_require_sponsor_filters_non_sponsors():
    cv = load_cv(DATA / "cv_sample.yaml")
    config = Config()
    h1b = load_default_index(DATA)
    jobs = run(cv, config, h1b_index=h1b, offline=True,
               require_h1b_sponsor=True)
    for j in jobs:
        if j.region == "us_h1b":
            assert j.sponsors_h1b is True


def test_write_drafts_creates_files_and_never_submits(tmp_path):
    cv = load_cv(DATA / "cv_sample.yaml")
    config = Config()
    jobs = run(cv, config, h1b_index=load_default_index(DATA), offline=True)
    folders = write_drafts(cv, jobs[:2], tmp_path, config)
    assert folders
    for folder in folders:
        assert (folder / "tailored_cv.md").exists()
        assert (folder / "cover_letter.txt").exists()
        assert (folder / "APPLY.md").exists()
        form = json.loads((folder / "application_form.json").read_text())
        # Draft marker present; nothing auto-submitted.
        assert "DRAFT ONLY" in form["_note"]
        assert form["requires_visa_sponsorship"] is None
