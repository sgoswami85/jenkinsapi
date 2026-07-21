# Relay — iPhone web app

A fully **on-device** version of the pipeline, built for phone use (no terminal
needed). It runs entirely client-side in the browser: your CV and jobs live in
`localStorage`, matching/tailoring happen in JavaScript, nothing is sent to a
server.

- **Keep your CV** on the device (there's a "Load sample" starter).
- **Paste jobs** you spot in the LinkedIn/Indeed apps, tagged by market
  (US·H1B, English-speaking Europe, Singapore, Australia).
- **Instant match scores** against your CV, plus an H1B-sponsor flag (name-match
  against a starter list — verify in DOL data) and an English-language check for
  European roles.
- **Tailored CV + cover letter** per job, ready to **Copy** or **Save** (the
  Save button uses the Artifact `downloads` capability).

It mirrors the Python package's logic (same TF-IDF/cosine scorer, same
skill-reordering tailor that never invents experience). Live API scanning is not
possible in a sandboxed browser page (CSP blocks outbound calls) — for automated
scanning across job boards, run the Python CLI (`../README.md`) on a computer.

## Viewing / editing

`app.html` is the source rendered by the hosted Artifact. It is written as
page content (styles + markup + script) to be wrapped at publish time, so open
it via the published Artifact link rather than the raw file. To change it, edit
`app.html` and republish to the same artifact URL.
