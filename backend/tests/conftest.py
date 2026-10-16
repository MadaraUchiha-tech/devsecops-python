import os

# Never touch a real database from tests: point the app at in-memory SQLite before it is imported.
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SEED_DEMO_DATA"] = "false"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app import models  # noqa: E402,F401
from app.db import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402

test_engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestSession = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client():
    """Fresh schema for every test so tests never depend on each other."""
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def doctor(client):
    return client.post(
        "/api/doctors", json={"full_name": "Dr. Test House", "specialty": "Cardiology", "room": "12"}
    ).json()


@pytest.fixture()
def patient(client):
    return client.post(
        "/api/patients", json={"full_name": "Jane Patient", "email": "jane@example.com", "phone": "555"}
    ).json()


@pytest.fixture()
def appointment(client, doctor, patient):
    return client.post(
        "/api/appointments",
        json={
            "patient_id": patient["id"],
            "doctor_id": doctor["id"],
            "scheduled_at": "2030-01-15T10:00:00Z",
            "duration_minutes": 30,
            "reason": "Routine check",
        },
    ).json()
