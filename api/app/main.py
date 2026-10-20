from fastapi import FastAPI

from app import errors

app = FastAPI(title="Aircon Sales API")
errors.install(app)


@app.get("/health")
def health():
    return {"status": "ok"}
