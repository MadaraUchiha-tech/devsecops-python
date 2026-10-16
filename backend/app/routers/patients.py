from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Patient
from ..schemas import PatientCreate, PatientOut, PatientUpdate

router = APIRouter(prefix="/api/patients", tags=["patients"])


def _get_or_404(db: Session, patient_id: int) -> Patient:
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


def _commit_unique(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A patient with this email already exists") from None


@router.get("", response_model=list[PatientOut])
def list_patients(q: str | None = None, db: Session = Depends(get_db)):
    query = select(Patient).order_by(Patient.full_name)
    if q:
        like = f"%{q}%"
        query = query.where(or_(Patient.full_name.ilike(like), Patient.email.ilike(like)))
    return list(db.scalars(query))


@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, patient_id)


@router.post("", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)):
    patient = Patient(**payload.model_dump())
    db.add(patient)
    _commit_unique(db)
    db.refresh(patient)
    return patient


@router.put("/{patient_id}", response_model=PatientOut)
def update_patient(patient_id: int, payload: PatientUpdate, db: Session = Depends(get_db)):
    patient = _get_or_404(db, patient_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(patient, key, value)
    _commit_unique(db)
    db.refresh(patient)
    return patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = _get_or_404(db, patient_id)
    db.delete(patient)
    db.commit()
