from fastapi import FastAPI

from app import auth, dashboard, errors

app = FastAPI(title="Aircon Sales API")
errors.install(app)
app.include_router(auth.router)
app.include_router(dashboard.router)


@app.get("/health")
def health():
    return {"status": "ok"}
