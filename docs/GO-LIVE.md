# Go-live checklist (VPS)

The steps for the day real sales data starts. The owner runs them with Claude Code on the VPS, in order.
Each step says what you should see. If a step doesn't show that, **stop** and go to [Roll back](#roll-back).

Written in task 3.5. Nothing here has been switched to production yet.

**What go-live does:** new secrets, `APP_ENV=production`, a brand-new **empty** database (the fake data is deleted),
real logins, a checked backup and a restore drill. The API stays on `127.0.0.1:8000` (not on the internet) until task 3.6.

All commands run from `~/aircon-sales/api` as `administrator`. If `docker` says "permission denied", run the
command as `sg docker -c "<command>"`.

---

## A. Before the day

1. **Decide the real users.** For each person: username, full name, role (`owner` or `sales`).
   Each person picks a password of at least 10 characters. Nobody shares a login.
2. **Have a password manager ready** (or a sealed paper copy kept by the owner). Step 7 creates the new database
   password; it should be kept somewhere other than the VPS.
3. **Tell the phones.** Anyone logged in with a fake-data account will be logged out at step 8 (new JWT secret).

## B. On the day

### 1. Latest code, all tests pass

```
cd ~/aircon-sales && git pull --rebase
cd api && .venv/bin/pip install -q -r requirements-dev.txt
.venv/bin/pytest -q
```
See: `… passed`, nothing failed.

### 2. Final backup of the fake data, moved aside

```
./scripts/backup.sh
mkdir -p ~/aircon-backups/dev-before-golive
mv ~/aircon-backups/aircon-*.dump ~/aircon-backups/dev-before-golive/
ls ~/aircon-backups ~/aircon-backups/dev-before-golive
```
See: `backup OK`, then no `aircon-*.dump` left directly in `~/aircon-backups` (they're in `dev-before-golive/`).
Why: backup retention keeps the first dump of each month, so a fake-data dump would otherwise be kept as this month's monthly.
Only `~/aircon-backups/aircon-*.dump` counts for retention; the sub-folder is ignored.

### 3. Keep the current settings for roll-back

```
cp .env ~/aircon-backups/env.dev-backup && chmod 600 ~/aircon-backups/env.dev-backup
```
Outside the repo on purpose: a copy inside `api/` would not be gitignored and would be copied into the Docker image.

### 4. Stop the API and database

```
docker compose down
```
See: `aircon-api` and `aircon-db` removed. (`down` without `-v` keeps the data volume; the next step removes it.)

### 5. Delete the fake-data database

Check the step-2 dump exists first: `ls -l ~/aircon-backups/dev-before-golive/`. Then:
```
docker volume rm aircon_aircon-pgdata
```
**Only this volume.** Never remove other volumes or containers on this VPS (D21).

### 6. New secrets, production mode

This writes new random secrets into `.env` without printing them:
```
PGPW=$(python3 -c 'import secrets; print(secrets.token_urlsafe(24))')
JWT=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
sed -i -e "s|^APP_ENV=.*|APP_ENV=production|" \
       -e "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$PGPW|" \
       -e "s|aircon:[^@]*@|aircon:$PGPW@|g" \
       -e "s|^JWT_SECRET=.*|JWT_SECRET=$JWT|" .env
unset PGPW JWT
chmod 600 .env
grep -E '^(APP_ENV|TRUSTED_PROXIES)=' .env
```
See: `APP_ENV=production` and `TRUSTED_PROXIES=` (empty until 3.6).
If `.env` has no `TRUSTED_PROXIES` line, that's fine (empty is the default).

### 7. Save the database password

```
grep '^POSTGRES_PASSWORD=' .env
```
Copy the value into the password manager, then clear the screen (`clear`). It's only needed to rebuild the server.
The JWT secret doesn't need saving: if it's lost, make a new one; everyone just logs in again.

### 8. Start with an empty database

```
docker compose up -d --build
sleep 20; docker ps --filter name=aircon --format '{{.Names}} {{.Status}}'
curl -s 127.0.0.1:8000/health; echo
curl -s -o /dev/null -w 'docs %{http_code}\n' 127.0.0.1:8000/docs
docker exec aircon-db psql -U aircon -d aircon -tAc 'select version_num from alembic_version; select count(*) from users; select count(*) from sales'
```
See: both containers `(healthy)`; `{"status":"ok"}`; `docs 404`; then the latest migration (`0002` today), `0`, `0`.
The new volume also gets a new, empty `aircon_test` (for the tests).

### 9. Make sure fake data can't come back

```
.venv/bin/python scripts/seed.py --reset; echo "exit $?"
```
See: `Refusing --reset with APP_ENV=production.` and `exit 1`. **Never** run `seed.py` without `--reset` on this server either.

### 10. Create the real users

Once per person (they type their own password, twice; it's never shown):
```
docker exec -it aircon-api python scripts/create_user.py --username <name> --full-name "<Full Name>" --role owner
docker exec -it aircon-api python scripts/create_user.py --username <name> --full-name "<Full Name>" --role sales
```
See: `Created <name> (<role>).` A wrong or short password is refused; just run it again.

### 11. Each user can log in

The password is read hidden and sent through a pipe, so it's not in the shell history or `ps`:
```
read -rsp 'Password: ' PW; echo
printf '{"username":"%s","password":"%s"}' <name> "$PW" | \
  curl -s -o /dev/null -w 'login %{http_code}\n' -H 'content-type: application/json' --data @- 127.0.0.1:8000/auth/login
unset PW
```
See: `login 200`. (`401` = wrong password; `429` = 5 wrong tries, wait 15 minutes or see `api/README.md` → Login rate limit.)

### 12. Backup works on the real database

```
./scripts/backup.sh
cat ~/aircon-backups/LAST_OK; ls ~/aircon-backups/LAST_FAILED 2>/dev/null || echo 'no LAST_FAILED'
crontab -l | grep backup.sh
```
See: `backup OK: …`, a timestamp, `no LAST_FAILED`, and the cron line `0 20 * * * …/backup.sh …` (02:30 Yangon).

### 13. Restore drill

```
./scripts/restore_check.sh "$(ls -1 ~/aircon-backups/aircon-*.dump | tail -1)"
```
See: `restore check OK: all row counts match` (`users` = the number of people from step 10).
This restores into a scratch database and drops it; the real one is not touched.

### 14. Tests still pass in production mode

The tests only use `aircon_test`, but some need development mode, so set it for the test run only:
```
APP_ENV=development .venv/bin/pytest -q
```
See: all passed. (Without `APP_ENV=development`, the docs test fails and the seed tests refuse to run: that's the
production safety working, not a bug.)

### 15. Done

Tell the planner: date and time of go-live, the number of users created, and the `LAST_OK` time.
From now on: never remove the `aircon_aircon-pgdata` volume, never run `docker compose down -v`.

---

## Roll back

**Before any real sale has been entered** (steps 4–14 went wrong), go back to the fake-data setup:
```
docker compose down
docker volume rm aircon_aircon-pgdata
cp ~/aircon-backups/env.dev-backup .env
docker compose up -d --build
docker exec -i aircon-db pg_restore -U aircon -d aircon --clean --if-exists --no-owner --exit-on-error \
  < "$(ls -1 ~/aircon-backups/dev-before-golive/aircon-*.dump | tail -1)"
curl -s 127.0.0.1:8000/health
```
(Or `.venv/bin/python scripts/seed.py --reset` instead of `pg_restore`, once `.env` says development again.)
Then fix the problem and start again at step 1.

**After real sales exist**, never delete the volume.
- A bad code update: `git log --oneline`, `git checkout <last good commit> -- .`, `docker compose up -d --build`,
  check `/health`. Then tell the planner.
- Lost or broken data: restore the newest good dump with `api/README.md` → "Restore for real" (it backs up first).
- Wrong user / password: `create_user.py` again (new password), or `--deactivate`.

---

## Before exposing to the internet (task 3.6)

Today the API only listens on `127.0.0.1:8000`; phones reach it through the SSH tunnel. Before phones can use it
over the internet, 3.6 needs from the owner:

1. **A domain name** (e.g. `api.<your-shop>.com`), and who controls its DNS.
2. **Which way in:**
   - **Cloudflare Tunnel**: no open ports on the VPS; needs the domain on a (free) Cloudflare account.
   - **Nginx + Let's Encrypt**: needs ports 80 and 443 open to the internet (free on this VPS today; check the
     hosting provider's firewall too), and an email for certificate expiry notices.
3. **OK to run a proxy** (`cloudflared` or Nginx) on this VPS next to the other projects, without touching theirs (D21).
4. Then 3.6 must set `TRUSTED_PROXIES` to the proxy's address as the container sees it (the Docker gateway,
   `172.19.0.1` today), otherwise every phone shares one login-rate-limit counter (see report 3.3).
5. Still open, and better decided before real data piles up: **where the off-site backup copy goes** (D31 → task 3.7).
