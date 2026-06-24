---
name: job-application-assistant
status: live
version: 1.0.0
created: 2026-06-24
---

# Job Application Assistant Skill

**Status: live** — callable, tested, wired to the chat persona.

Helps the user research a job posting, tailor their resume highlights, and generate a
cover letter. Produces documents in the user workspace using the `generate_document`
tool (HTML, printable as PDF).

## What it actually does

- `analyze_job_posting(text_or_url)` — Extracts key requirements, responsibilities, and
  signals from a raw job posting text. Returns a structured `JobPostingAnalysis`.
- `tailor_highlights(analysis, background)` — Given a posting analysis and the user's
  background fields, returns a list of tailored bullet points for the resume experience
  section and a suggested opening sentence for the cover letter.
- `build_application_pack(name, background, analysis, output_dir)` — Orchestrates the
  full flow: tailors highlights → renders a resume HTML + cover letter HTML → writes both
  to the user workspace.

## Live tools used

- `generate_document` (tool-runner.js) — writes HTML/md to `~/.keystone/workspace/`
- `web_search` / `web_fetch` (tool-runner.js) — research the posting URL if provided
- Standard library only — no external packages required for core analysis

## Persona wiring

The `job_application` persona is registered in `apps/lantern-garage/lib/dream-chat.js`
and routes on keywords: `job`, `resume`, `cover letter`, `apply`, `application`,
`interview`, `hiring`, `recruiter`, `LinkedIn`, `offer`.

## Evidence / External Reality Rule

All tailoring logic uses the *user-supplied background fields* and the *extracted
posting text* — no fabricated experience is inserted. Bullet points are selected and
reframed from the user's own background, not invented.
