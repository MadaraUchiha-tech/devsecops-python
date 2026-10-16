import logging

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .config import settings
from .db import get_db
from .routers import appointments, doctors, patients

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


# Schema is owned by Alembic and demo data by `python -m app.seed`; both run before Uvicorn.
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Clinic appointment scheduling API: doctors, patients and appointments.",
)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_methods=["*"], allow_headers=["*"])
Instrumentator(excluded_handlers=["/metrics", "/health", "/ready"]).instrument(app).expose(
    app, endpoint="/metrics", include_in_schema=False
)

app.include_router(doctors.router)
app.include_router(patients.router)
app.include_router(appointments.router)


@app.get("/", tags=["meta"])
def root():
    return {"service": settings.app_name, "version": settings.app_version, "docs": "/docs"}


@app.get("/health", tags=["meta"])
def health():
    """Liveness: the process is up and serving HTTP."""
    return {"status": "UP"}


@app.get("/ready", tags=["meta"])
def ready(db: Session = Depends(get_db)):
    """Readiness: the database is reachable, so this pod can take traffic."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {"status": "READY"}
