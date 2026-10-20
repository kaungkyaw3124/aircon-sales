---
description: Pull the latest plan from GitHub and do the tasks in docs/NEXT.md, looping until each task's checks pass.
---

Run the task loop for this project.

1. `git pull` on `main`. If it fails, stop and report the error.
2. Read `CLAUDE.md`, `docs/PLAN.md`, `docs/DECISIONS.md` and `docs/NEXT.md`.
3. If `docs/NEXT.md` says `Status: WAITING`, there is nothing to do: say so and stop.
4. Do the tasks in `docs/NEXT.md` **in order**. For each task:
   - Check the **Machine** line. If this is the wrong machine (Windows PC vs VPS), stop and say which machine to run `/next` on.
   - Do the work, run every **Done when** check, fix and re-run until all pass.
     Follow the hard rules in `CLAUDE.md` (never weaken a test, stay in scope).
   - If you are stuck after a few honest attempts, or a business decision is needed, stop and mark the task BLOCKED.
   - Write `docs/reports/report-<task id>.md` in the format from `CLAUDE.md`.
   - Commit (work + report together) with message `task <id>: <title>` and push.
   - If the task says **Stop for review: yes**, stop after it, even if more tasks follow.
5. When you stop, update `docs/STATUS.md` (overwrite it):
   - last task done, its status (DONE / BLOCKED / NEEDS REVIEW), commit hash
   - the open questions for the owner (copied from the report)
   - which machine the next task needs
   Commit `docs/STATUS.md` with message `status: <task id>` and push.
6. Do **not** edit `docs/NEXT.md`, `docs/PLAN.md` or `docs/DECISIONS.md`. The planner writes those.
7. End with a short summary: tasks done, status, and "attach docs/reports/report-<id>.md to the planner".
