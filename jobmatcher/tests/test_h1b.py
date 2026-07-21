from jobmatcher.h1b import H1BSponsorIndex, normalize_company


def test_normalize_strips_suffixes():
    assert normalize_company("Acme Cloud, Inc.") == "acme cloud"
    assert normalize_company("Globex Corporation") == "globex"


def test_sponsor_exact_and_fuzzy():
    idx = H1BSponsorIndex(["Acme Cloud Inc", "Northwind Analytics LLC"])
    assert idx.sponsors("Acme Cloud") is True
    assert idx.sponsors("ACME CLOUD, INC.") is True
    assert idx.sponsors("Northwind Analytics") is True
    assert idx.sponsors("Totally Unrelated Co") is False


def test_from_csv(tmp_path):
    p = tmp_path / "s.csv"
    p.write_text("EMPLOYER_NAME\nAcme Cloud\nInitech\n", encoding="utf-8")
    idx = H1BSponsorIndex.from_csv(p)
    assert len(idx) == 2
    assert idx.sponsors("Initech") is True


def test_from_csv_no_header(tmp_path):
    p = tmp_path / "s.csv"
    p.write_text("Acme Cloud\nInitech\n", encoding="utf-8")
    idx = H1BSponsorIndex.from_csv(p)
    assert idx.sponsors("Acme Cloud") is True
