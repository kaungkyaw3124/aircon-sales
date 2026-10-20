---
description: Pull the latest plan from GitHub and do this machine's tasks in docs/NEXT.md, looping until each task's checks pass.
---

Run the task loop for this project.

1. Work out which machine this is: **Windows PC** (Windows OS, `D:\claude\p1`) or **VPS** (Linux, `~/aircon-sales`).
2. `git pull --rebase` on `main`. If it fails, stop and report the error.
3. Read `CLAUDE.md`, `docs/PLAN.md`, `docs/DECISIONS.md` and `docs/NEXT.md`.
4. `docs/NEXT.md` has one section per machine. Only do the tasks in **this machine's section**.
   The other machine may be working on its own section at the same time; never touch its files.
   If this machine's section says `Status: WAITING`, say so and stop.
5. Do this machine's tasks **in order**. For each task:
   - Skip a task whose report already says DONE (`docs/reports/report-<id>.md`).
   - Do the work, run every **Done when** check, fix and re-run until all pass.
     Follow the hard rules in `CLAUDE.md` (never weaken a test, stay in scope, never change `openapi.yaml`).
   - If you are stuck after a few honest attempts, or a business decision is needed, stop and mark the task BLOCKED.
   - Write `docs/reports/report-<task id>.md` in the format from `CLAUDE.md`.
   - Commit (work + report together) with message `task <id>: <title>`, then `git pull --rebase` and push.
   - If the task says **Stop for review: yes**, stop after it, even if more tasks follow.
6. When you stop, overwrite **this machine's** status file: `docs/status/vps.md` or `docs/status/windows.md`:
   - last task done, its status (DONE / BLOCKED / NEEDS REVIEW), commit hash
   - the open questions for the owner (copied from the report)
   - facts the planner should know (ports, versions, anything surprising)
   Commit with message `status: <task id>`, `git pull --rebase`, push.
7. Do **not** edit `docs/NEXT.md`, `docs/PLAN.md` or `docs/DECISIONS.md`. The planner writes those.
8. End with a short summary: tasks done, status, and "tell the planner: check report".
