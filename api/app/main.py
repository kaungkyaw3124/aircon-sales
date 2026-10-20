from fastapi import FastAPI

app = FastAPI(title="Aircon Sales API")


@app.get("/health")
def health():
    return {"status": "ok"}
