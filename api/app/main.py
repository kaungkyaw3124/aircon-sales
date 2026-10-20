import logging
import sys
import time

from fastapi import FastAPI, Request

from app import auth, dashboard, errors

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
access_log = logging.getLogger("app.access")

app = FastAPI(title="Aircon Sales API")
errors.install(app)
app.include_router(auth.router)
app.include_router(dashboard.router)


@app.middleware("http")
async def log_request(request: Request, call_next):
    # Path only: no query string, headers or body, so tokens and passwords never reach the log.
    start = time.perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        if request.url.path != "/health":  # the Docker healthcheck calls it every 10 s
            ms = (time.perf_counter() - start) * 1000
            access_log.info("%s %s %d %.1fms", request.method, request.url.path, status, ms)


@app.get("/health")
def health():
    return {"status": "ok"}
