from fastapi import FastAPI

app = FastAPI(title="MiMedidor API")


@app.get("/api/salud")
def salud() -> dict[str, str]:
    """Endpoint mínimo para que el pipeline de CI (T-05) tenga algo real que probar."""
    return {"estado": "ok"}
