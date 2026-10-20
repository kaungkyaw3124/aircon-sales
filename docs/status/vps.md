# Status: VPS

Overwritten by Claude Code at the end of every `/next` run.

- **Last task:** 0.5 — Fake data generator
- **Status:** NEEDS REVIEW (all checks pass; stopped for review at the end of Phase 0, as the task requires)
- **Commit:** 008a1b8
- **Also done this run:** 0.4 — Database + API skeleton, DONE, commit c6fcf8f
- **VPS facts:** our Postgres is on `127.0.0.1:5433` (5432 belongs to another project) and the API is on `127.0.0.1:8000`.
  The owner added `administrator` to the `docker` group and installed `python3.14-venv`. Python on the VPS is 3.14.
- **Open questions (from report-0.5):**
  1. Seeded "today" covers the whole day 09:00–19:00, so right after a seed some of today's sales are later than the current time. OK for dev data?
- **Next machine:** **VPS** for Phase 1 (backend). Phase 2 (Android) can run on the **Windows PC**.
