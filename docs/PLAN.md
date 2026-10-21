# Plan

Roadmap for the Aircon Sales Dashboard. Written by the planner (Claude chat).
Claude Code reads this but does not edit it. Progress lives in `docs/status/` and `docs/reports/`.

## How the loop works

```
Planner (Claude chat)              GitHub repo                  Claude Code (Windows PC / VPS)
writes PLAN, DECISIONS, NEXT  ──►  docs/NEXT.md  ──►  /next  ──►  pull, do tasks, test, fix, loop
reads report, writes next NEXT ◄── docs/reports/ + status/   ◄──  report, commit, push
```

Owner's part: run `/next` on each machine that has tasks in `docs/NEXT.md` (both can run at the same time), then tell the planner "check report".
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
- [x] 0.4 Database + API skeleton on VPS (Postgres 127.0.0.1:5433, API 127.0.0.1:8000)
- [x] 0.5 Fake data generator (499 sales / 90 days)

### Phase 1 — Backend MVP (VPS)
- [x] 1.1 Error handling (shared error shape)
- [x] 1.2 Login with JWT
- [x] 1.3 `GET /dashboard/today`
- [x] 1.4 "Today" in Asia/Yangon (boundary tests)
- [x] 1.5 Contract tests (Schemathesis)

### Phase 2 — Android MVP (Windows) — can start after 0.3 is approved
- [x] 2.1 Dependencies + app structure
- [x] 2.2 API client matching the contract
- [x] 2.3 Login screen + saved token
- [x] 2.4 Today dashboard screen
- [x] 2.5 Loading, error, offline states
- [x] Owner ran the app on a Xiaomi phone (USB + SSH tunnel) — approved (D27)
- [x] 2.6 Verify debug-URL change (D26) + "run on phone" guide and script
- [x] 2.7 Fixed brand colours (D28) + no Android backup of the token (D29)
- [x] 2.8 Compose previews in Android Studio

### Phase 3 — Deploy (VPS)
- [x] 3.1 Production-ready container (runtime-only image, auto-migrate, healthcheck, request logs)
- [x] 3.2 Daily database backup + restore test
- [ ] 3.3 Login rate limiting (contract v0.1.1: 429) + Windows 2.9 (app handles 429)
- [ ] 3.4 Production hardening (docs off, log rotation, create-user script, monthly backups)
- [ ] 3.5 Go-live checklist (`docs/GO-LIVE.md`)
- [ ] 2.10 Neutral backgrounds + R8 release build
- [ ] 3.6 Expose the API to phones over HTTPS — **needs owner answers**: domain? Cloudflare Tunnel or Nginx + Let's Encrypt?
- [ ] 3.7 Off-site backup copy — **needs owner answer**: where?
- [ ] 3.8 App release build points to the real server, signed APK for the owner's phone

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
