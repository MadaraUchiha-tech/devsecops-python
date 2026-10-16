"""Demo data for a fresh database. Only runs when SEED_DEMO_DATA=true and the tables are empty."""

from datetime import UTC, date, datetime, time, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import Appointment, Doctor, Patient

DOCTORS = [
    ("Dr. Aisha Mehta", "General Medicine", "101"),
    ("Dr. Rohan Kapoor", "Cardiology", "204"),
    ("Dr. Sara Fernandes", "Pediatrics", "108"),
    ("Dr. Vikram Rao", "Dermatology", "305"),
    ("Dr. Leena Joshi", "Orthopedics", "210"),
]
PATIENTS = [
    ("Arjun Sharma", "arjun.sharma@example.com", "+91 98200 11111", date(1988, 4, 12)),
    ("Priya Nair", "priya.nair@example.com", "+91 98200 22222", date(1995, 9, 3)),
    ("Kabir Singh", "kabir.singh@example.com", "+91 98200 33333", date(2016, 1, 21)),
    ("Meera Iyer", "meera.iyer@example.com", "+91 98200 44444", date(1972, 6, 30)),
    ("Dev Patel", "dev.patel@example.com", "+91 98200 55555", date(2001, 11, 8)),
    ("Ananya Gupta", "ananya.gupta@example.com", "+91 98200 66666", date(1990, 2, 17)),
]
# (patient index, doctor index, day offset, hour, minute, reason, status)
APPOINTMENTS = [
    (0, 0, 0, 9, 0, "Annual check-up", "COMPLETED"),
    (1, 1, 0, 10, 30, "Chest pain follow-up", "CHECKED_IN"),
    (2, 2, 0, 11, 0, "Vaccination", "SCHEDULED"),
    (3, 4, 0, 14, 0, "Knee pain", "SCHEDULED"),
    (4, 3, 0, 15, 30, "Skin rash", "CANCELLED"),
    (5, 0, 1, 9, 30, "Fever and cough", "SCHEDULED"),
    (0, 1, 1, 12, 0, "ECG review", "SCHEDULED"),
    (3, 2, -1, 10, 0, "Grandchild consult", "NO_SHOW"),
]


def seed_demo_data(db: Session) -> bool:
    if db.scalar(select(func.count(Doctor.id))):
        return False
    doctors = [Doctor(full_name=n, specialty=s, room=r) for n, s, r in DOCTORS]
    patients = [Patient(full_name=n, email=e, phone=p, date_of_birth=d) for n, e, p, d in PATIENTS]
    db.add_all(doctors + patients)
    db.flush()
    today = datetime.now(UTC).date()
    for p, d, offset, hour, minute, reason, status in APPOINTMENTS:
        when = datetime.combine(today + timedelta(days=offset), time(hour, minute), tzinfo=UTC)
        db.add(
            Appointment(
                patient_id=patients[p].id, doctor_id=doctors[d].id, scheduled_at=when, reason=reason, status=status
            )
        )
    db.commit()
    return True
