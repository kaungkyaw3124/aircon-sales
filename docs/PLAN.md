# Plan

Roadmap for the Aircon Sales Dashboard. Written by the planner (Claude chat).
Claude Code reads this but does not edit it. Progress lives in `docs/STATUS.md` and `docs/reports/`.

## How the loop works

```
Planner (Claude chat)              GitHub repo                  Claude Code (Windows PC / VPS)
writes PLAN, DECISIONS, NEXT  ──►  docs/NEXT.md  ──►  /next  ──►  pull, do tasks, test, fix, loop
reads report, writes next NEXT ◄── docs/reports/ + STATUS.md  ◄──  report, commit, push
```

Owner's part: run `/next` on the machine `docs/STATUS.md` names, then attach the report to the planner.
Business decisions go into `docs/DECISIONS.md`.

## Machines

- **Windows PC** (`D:\claude\p1`): Android app, docs.
- **VPS** (`~/aircon-sales`): API + PostgreSQL, docs.

## Phases

### Phase 0 — Foundations
- [x] 0.1 Project structure + GitHub
- [x] 0.2 Database design (+ 0.2b owner decisions)
- [x] 0.2c Schema follow-ups (D13–D15)
- [x] 0.3 API contract (`openapi.yaml`) — approved (D19)
- [ ] 0.4 Database + API skeleton on VPS
- [ ] 0.5 Fake data generator

### Phase 1 — Backend MVP (VPS)
- [ ] 1.1 FastAPI app + `/health`
- [ ] 1.2 Login with JWT
- [ ] 1.3 `GET /dashboard/today`
- [ ] 1.4 "Today" in Asia/Yangon (boundary tests)
- [ ] 1.5 Contract tests (Schemathesis)

### Phase 2 — Android MVP (Windows) — can start after 0.3 is approved
- [ ] 2.1 Dependencies + app structure
- [ ] 2.2 API client matching the contract
- [ ] 2.3 Login screen + saved token
- [ ] 2.4 Today dashboard screen
- [ ] 2.5 Loading, error, offline states
- [ ] 2.6 Owner installs the APK and approves

### Phase 3 — Deploy (VPS)
- [ ] 3.1 Docker Compose production setup
- [ ] 3.2 Nginx + HTTPS + firewall
- [ ] 3.3 Daily database backup + restore test
- [ ] 3.4 App release build points to the real server

### Phase 4 — Reports and charts
- [ ] Date ranges, top products, by salesperson, payment methods
- [ ] Charts in the app

### Phase 5 — Roles, stock, notifications
- [ ] Owner / sales permissions enforced
- [ ] Stock levels + low-stock alerts
- [ ] Push notifications

### Phase 6 — Real data
- [ ] Sales entry (app or web admin) or import from the current system
- [ ] Production database with real data only
