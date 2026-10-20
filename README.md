# Aircon Sales Dashboard

Android app showing sales data for an aircon and accessories business. The app reads data from an API server running on a VPS.

## Layout

```
/android   Android app (Kotlin + Jetpack Compose) — built on the Windows PC
/api       API server (Python FastAPI + PostgreSQL) — runs on the VPS
/docs      Contract, schema, goals
  openapi.yaml      API contract: the single source of truth
  schema.md         Database design notes
  goals/            One goal file per step (phase-0.md, phase-1.md, ...)
```

See `CLAUDE.md` for how work is organised, commands and business rules.
