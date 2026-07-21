# jobmatcher

A **compliant** job-match + CV-tailoring pipeline. It scans legitimate job-board
APIs across four target markets, scores each opening against your CV, tailors
the CV per role you pick, and prepares application drafts for you to review and
submit.

It does **not** scrape LinkedIn, and it does **not** auto-submit applications —
both for good reasons (see [Why not LinkedIn scraping?](#why-not-linkedin-scraping)).

## Target markets

| Region bucket      | Countries covered                     | Special handling |
|--------------------|---------------------------------------|------------------|
| `us_h1b`           | US                                    | Flags employers found in public **DOL H1B (LCA)** sponsor data |
| `europe_english`   | UK, Netherlands, Germany, Switzerland, Austria | English-language heuristic filters out roles requiring local fluency |
| `singapore`        | Singapore                             | — |
| `australia`        | Australia                             | — |

## Install

```bash
cd jobmatcher
pip install -r requirements.txt
# optional, for LLM-assisted summary tailoring:
# pip install anthropic
```

## Quick start (offline, no keys)

```bash
python -m jobmatcher search --cv data/cv_sample.yaml --offline
```

You'll get a ranked shortlist using bundled synthetic data — enough to see how
scoring, region bucketing, and H1B annotation work.

## Live search

1. Get free Adzuna API credentials at <https://developer.adzuna.com/>.
2. Set them (or copy `.env.example` to `.env` and fill in):
   ```bash
   export ADZUNA_APP_ID=...   ADZUNA_APP_KEY=...
   ```
3. Point it at **your** CV and run:
   ```bash
   python -m jobmatcher search --cv my_cv.yaml \
       --regions us_h1b,europe_english,singapore,australia
   ```

### Real H1B sponsor data

The bundled `data/h1b_sponsors_sample.csv` is a tiny placeholder. For real
filtering, download the DOL LCA disclosure data (an employer column named
`EMPLOYER_NAME`) from
<https://www.dol.gov/agencies/eta/foreign-labor/performance> and pass it:

```bash
python -m jobmatcher search --cv my_cv.yaml \
    --h1b-csv data/h1b_sponsors.csv --require-sponsor
```

`--require-sponsor` keeps only US employers that appear in that data.

## Prepare application drafts

Pick the 1-based indexes you liked from `search`, then:

```bash
python -m jobmatcher apply --cv my_cv.yaml --select 1,3,4 --out out/
```

Each job gets its own folder under `out/` containing:

- `tailored_cv.md` — your CV with the skills the job mentions surfaced first
  (nothing invented — only re-emphasized).
- `cover_letter.txt` — a factual, role-specific cover letter.
- `application_form.json` — common ATS fields (name, email, links…) pre-filled
  from your CV for you to paste into the real portal. **Draft only.**
- `APPLY.md` — the apply link, H1B note, and a manual submit checklist.

**Nothing is submitted anywhere.** The apply link opens the employer's own
portal, where you review everything and click submit yourself.

## Your CV format

A CV is a YAML (or JSON) file — see `data/cv_sample.yaml`. Copy it to
`my_cv.yaml` (git-ignored) and fill in your real details and `target_titles`.

## Optional: LLM-assisted tailoring

If `ANTHROPIC_API_KEY` is set, the summary is rewritten to emphasize relevant
strengths — under a strict instruction to **never invent** experience, only
re-emphasize what's already in your CV. Without a key, a transparent
deterministic path is used instead.

## Why not LinkedIn scraping?

LinkedIn's Terms of Service prohibit automated scraping, they enforce it with
bot detection and account bans, and their official API offers no general
job-search endpoint. Building on scraping would be fragile, risk getting *your*
account restricted, and carry legal exposure. This project uses documented,
terms-compliant job-board APIs instead — reliable and safe.

Likewise, auto-submitting applications to third-party portals (Workday,
Greenhouse, Lever, company sites) violates most of their terms, trips CAPTCHAs,
and risks sending unreviewed content. So this tool prepares drafts and stops at
the submit button, which stays yours to press.

## Architecture

```
search_jobs ──> annotate_and_filter ──> score_jobs ──> shortlist ──> write_drafts
 (sources/)      (h1b + english)         (matching)                   (tailor +
                                                                       coverletter)
```

- `sources/` — pluggable job sources (`adzuna`, offline `sample`). Add more by
  implementing the `JobSource` protocol.
- `h1b.py` — normalized employer-name matching against DOL sponsor data.
- `matching.py` — dependency-free TF-IDF + cosine scoring; English-language
  heuristic for continental Europe.
- `tailor.py` / `coverletter.py` — per-job CV/letter generation.
- `drafts.py` — writes the review-and-submit application folders.

## Tests

```bash
python -m pytest -q
```

## Scope / honesty

This is a starting pipeline, not a magic auto-apply bot. The English-language
filter is heuristic, sponsor matching is name-based (verify before applying),
and you always review and submit each application yourself.
