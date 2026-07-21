from jobmatcher.models import CV, Job
from jobmatcher.matching import score_jobs, looks_english


def _cv():
    return CV(
        name="Test",
        headline="Backend Engineer",
        email="t@example.com",
        skills=["Python", "AWS", "Kubernetes", "PostgreSQL"],
        target_titles=["Backend Engineer"],
        summary="Python backend engineer with AWS and Kubernetes.",
    )


def _job(jid, title, desc, country="us", region="us_h1b"):
    return Job(
        source="sample", source_id=jid, title=title, company="C",
        location="X", country=country, region=region, description=desc,
        url="http://x",
    )


def test_relevant_job_scores_higher():
    cv = _cv()
    jobs = [
        _job("1", "Frontend Designer",
             "Figma, CSS, brand design and typography work."),
        _job("2", "Backend Engineer",
             "Python, AWS, Kubernetes and PostgreSQL microservices."),
    ]
    ranked = score_jobs(cv, jobs)
    assert ranked[0].source_id == "2"
    assert ranked[0].match_score > ranked[1].match_score


def test_matched_terms_populated():
    cv = _cv()
    jobs = [_job("2", "Backend Engineer", "Python AWS Kubernetes PostgreSQL")]
    score_jobs(cv, jobs)
    assert "python" in jobs[0].matched_terms


def test_english_native_markets_pass():
    for country in ("us", "gb", "au", "sg"):
        job = _job("x", "Engineer", "Some role", country=country,
                   region="europe_english")
        assert looks_english(job) is True


def test_continental_requires_english_signal():
    yes = _job("1", "Backend Developer",
               "Our working language is English. Relocation supported.",
               country="nl", region="europe_english")
    no = _job("2", "Entwickler",
              "Fließend Deutsch erforderlich. Deutschkenntnisse.",
              country="de", region="europe_english")
    assert looks_english(yes) is True
    assert looks_english(no) is False
