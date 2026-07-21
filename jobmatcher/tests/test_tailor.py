from jobmatcher.models import CV, Job
from jobmatcher.tailor import tailor_cv, reorder_skills
from jobmatcher.coverletter import cover_letter


def _cv():
    return CV(
        name="Jane Doe",
        headline="Backend Engineer",
        email="j@example.com",
        skills=["Photoshop", "Python", "Excel", "AWS"],
        summary="Engineer.",
    )


def _job():
    return Job(
        source="s", source_id="1", title="Python Engineer", company="Acme",
        location="NYC", country="us", region="us_h1b",
        description="We need Python and AWS skills.", url="http://x",
    )


def test_reorder_surfaces_matching_skills_first():
    ordered = reorder_skills(_cv(), _job())
    assert ordered[:2] == ["Python", "AWS"]
    assert set(ordered) == {"Photoshop", "Python", "Excel", "AWS"}


def test_tailor_does_not_mutate_input_and_adds_focus():
    cv = _cv()
    tailored = tailor_cv(cv, _job())
    assert cv.skills == ["Photoshop", "Python", "Excel", "AWS"]  # unchanged
    assert tailored.skills[:2] == ["Python", "AWS"]
    assert "Python Engineer" in tailored.headline
    assert "Python" in tailored.summary


def test_tailor_invents_nothing():
    cv = _cv()
    tailored = tailor_cv(cv, _job())
    # No new skills introduced.
    assert set(tailored.skills) == set(cv.skills)


def test_cover_letter_mentions_company_and_role():
    letter = cover_letter(_cv(), _job())
    assert "Acme" in letter
    assert "Python Engineer" in letter
    assert "Jane Doe" in letter
