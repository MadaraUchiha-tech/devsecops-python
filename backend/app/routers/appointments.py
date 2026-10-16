from datetime import UTC, date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from .. import metrics
from ..db import get_db
from ..models import Appointment, Doctor, Patient
from ..schemas import (
    AppointmentCreate,
    AppointmentOut,
    AppointmentStats,
    AppointmentStatus,
    AppointmentUpdate,
    DoctorLoad,
)

router = APIRouter(prefix="/api/appointments", tags=["appointments"])

# Which status an appointment may move to from its current one.
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "SCHEDULED": {"CHECKED_IN", "CANCELLED", "NO_SHOW"},
    "CHECKED_IN": {"COMPLETED", "CANCELLED"},
    "COMPLETED": set(),
    "CANCELLED": set(),
    "NO_SHOW": set(),
}
INACTIVE_STATUSES = ("CANCELLED", "NO_SHOW")


def _as_utc(value: datetime) -> datetime:
    # SQLite drops tzinfo; PostgreSQL keeps it. Normalise so comparisons work on both.
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


def _to_out(appt: Appointment) -> AppointmentOut:
    return AppointmentOut(
        id=appt.id,
        patient_id=appt.patient_id,
        doctor_id=appt.doctor_id,
        patient_name=appt.patient.full_name,
        doctor_name=appt.doctor.full_name,
        specialty=appt.doctor.specialty,
        scheduled_at=_as_utc(appt.scheduled_at),
        duration_minutes=appt.duration_minutes,
        reason=appt.reason,
        status=appt.status,
        notes=appt.notes,
        created_at=_as_utc(appt.created_at),
        updated_at=_as_utc(appt.updated_at),
    )


def _get_or_404(db: Session, appointment_id: int) -> Appointment:
    appt = db.get(
        Appointment, appointment_id, options=[joinedload(Appointment.patient), joinedload(Appointment.doctor)]
    )
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appt


def _ensure_slot_free(
    db: Session, doctor_id: int, start: datetime, duration: int, ignore_id: int | None = None
) -> None:
    """Reject the booking if it overlaps another active appointment for the same doctor."""
    start = _as_utc(start)
    end = start + timedelta(minutes=duration)
    window_start = start - timedelta(hours=8)
    query = select(Appointment).where(
        Appointment.doctor_id == doctor_id,
        Appointment.status.not_in(INACTIVE_STATUSES),
        Appointment.scheduled_at >= window_start,
        Appointment.scheduled_at < end,
    )
    if ignore_id is not None:
        query = query.where(Appointment.id != ignore_id)
    for other in db.scalars(query):
        other_start = _as_utc(other.scheduled_at)
        other_end = other_start + timedelta(minutes=other.duration_minutes)
        if start < other_end and other_start < end:
            metrics.booking_conflicts.inc()
            raise HTTPException(
                status_code=409,
                detail=f"Doctor already has appointment #{other.id} at {other_start:%Y-%m-%d %H:%M} UTC",
            )


@router.get("", response_model=list[AppointmentOut])
def list_appointments(
    status_filter: AppointmentStatus | None = None,
    doctor_id: int | None = None,
    patient_id: int | None = None,
    on_date: date | None = None,
    db: Session = Depends(get_db),
):
    query = (
        select(Appointment)
        .options(joinedload(Appointment.patient), joinedload(Appointment.doctor))
        .order_by(Appointment.scheduled_at)
    )
    if status_filter:
        query = query.where(Appointment.status == status_filter)
    if doctor_id:
        query = query.where(Appointment.doctor_id == doctor_id)
    if patient_id:
        query = query.where(Appointment.patient_id == patient_id)
    if on_date:
        day_start = datetime.combine(on_date, time.min, tzinfo=UTC)
        query = query.where(
            Appointment.scheduled_at >= day_start, Appointment.scheduled_at < day_start + timedelta(days=1)
        )
    return [_to_out(a) for a in db.scalars(query)]


@router.get("/stats", response_model=AppointmentStats)
def appointment_stats(db: Session = Depends(get_db)):
    counts = dict(db.execute(select(Appointment.status, func.count(Appointment.id)).group_by(Appointment.status)).all())
    day_start = datetime.combine(datetime.now(UTC).date(), time.min, tzinfo=UTC)
    today = db.scalar(
        select(func.count(Appointment.id)).where(
            Appointment.scheduled_at >= day_start, Appointment.scheduled_at < day_start + timedelta(days=1)
        )
    )
    load_rows = db.execute(
        select(Doctor.id, Doctor.full_name, Doctor.specialty, func.count(Appointment.id))
        .outerjoin(
            Appointment,
            (Appointment.doctor_id == Doctor.id) & (Appointment.status.in_(("SCHEDULED", "CHECKED_IN"))),
        )
        .where(Doctor.active.is_(True))
        .group_by(Doctor.id, Doctor.full_name, Doctor.specialty)
        .order_by(func.count(Appointment.id).desc(), Doctor.full_name)
    ).all()
    return AppointmentStats(
        total=sum(counts.values()),
        today=today or 0,
        scheduled=counts.get("SCHEDULED", 0),
        checked_in=counts.get("CHECKED_IN", 0),
        completed=counts.get("COMPLETED", 0),
        cancelled=counts.get("CANCELLED", 0),
        no_show=counts.get("NO_SHOW", 0),
        patients=db.scalar(select(func.count(Patient.id))) or 0,
        active_doctors=len(load_rows),
        doctor_load=[DoctorLoad(doctor_id=r[0], doctor_name=r[1], specialty=r[2], upcoming=r[3]) for r in load_rows],
    )


@router.get("/{appointment_id}", response_model=AppointmentOut)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    return _to_out(_get_or_404(db, appointment_id))


@router.post("", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
def book_appointment(payload: AppointmentCreate, db: Session = Depends(get_db)):
    if not db.get(Patient, payload.patient_id):
        raise HTTPException(status_code=404, detail="Patient not found")
    doctor = db.get(Doctor, payload.doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    if not doctor.active:
        raise HTTPException(status_code=409, detail="Doctor is not accepting appointments")
    _ensure_slot_free(db, payload.doctor_id, payload.scheduled_at, payload.duration_minutes)

    data = payload.model_dump()
    data["scheduled_at"] = _as_utc(payload.scheduled_at)
    appt = Appointment(**data)
    db.add(appt)
    db.commit()
    metrics.appointments_booked.labels(specialty=doctor.specialty).inc()
    return _to_out(_get_or_404(db, appt.id))


@router.put("/{appointment_id}", response_model=AppointmentOut)
def update_appointment(appointment_id: int, payload: AppointmentUpdate, db: Session = Depends(get_db)):
    appt = _get_or_404(db, appointment_id)
    changes = payload.model_dump(exclude_unset=True)

    new_status = changes.get("status")
    if new_status and new_status != appt.status:
        if new_status not in ALLOWED_TRANSITIONS[appt.status]:
            raise HTTPException(status_code=409, detail=f"Cannot move appointment from {appt.status} to {new_status}")
        metrics.appointment_transitions.labels(to_status=new_status).inc()

    if "scheduled_at" in changes or "duration_minutes" in changes:
        if appt.status not in ("SCHEDULED",):
            raise HTTPException(status_code=409, detail="Only scheduled appointments can be rescheduled")
        start = changes.get("scheduled_at", appt.scheduled_at)
        duration = changes.get("duration_minutes", appt.duration_minutes)
        _ensure_slot_free(db, appt.doctor_id, start, duration, ignore_id=appt.id)
        if "scheduled_at" in changes:
            changes["scheduled_at"] = _as_utc(start)

    for key, value in changes.items():
        setattr(appt, key, value)
    db.commit()
    return _to_out(_get_or_404(db, appointment_id))


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appt = _get_or_404(db, appointment_id)
    db.delete(appt)
    db.commit()
