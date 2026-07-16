from datetime import date
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Medication
from ..templating import templates

router = APIRouter(prefix="/medications", tags=["medications"])


@router.get("/")
def list_medications(request: Request, db: Session = Depends(get_db)):
    meds = db.scalars(
        select(Medication).order_by(Medication.name, Medication.start_date.desc())
    ).all()
    active = [m for m in meds if m.end_date is None]
    history = [m for m in meds if m.end_date is not None]
    return templates.TemplateResponse(
        "medications.html", {"request": request, "active": active, "history": history}
    )


@router.post("/")
def add_medication(
    name: str = Form(...),
    dosage: str = Form(""),
    frequency: str = Form(""),
    purpose: str = Form(""),
    start_date: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    med = Medication(
        name=name,
        dosage=dosage or None,
        frequency=frequency or None,
        purpose=purpose or None,
        start_date=date.fromisoformat(start_date) if start_date else date.today(),
        notes=notes or None,
    )
    db.add(med)
    db.commit()
    return RedirectResponse("/medications/", status_code=303)


@router.post("/{med_id}/change")
def change_medication(
    med_id: int,
    dosage: str = Form(""),
    frequency: str = Form(""),
    change_reason: str = Form(""),
    effective_date: str = Form(""),
    db: Session = Depends(get_db),
):
    """Close the current medication row and start a new version, preserving history."""
    current = db.get(Medication, med_id)
    if current:
        change_date = date.fromisoformat(effective_date) if effective_date else date.today()
        current.end_date = change_date
        current.change_reason = change_reason or current.change_reason
        new_version = Medication(
            name=current.name,
            dosage=dosage or current.dosage,
            frequency=frequency or current.frequency,
            purpose=current.purpose,
            start_date=change_date,
            change_reason=change_reason or None,
            notes=current.notes,
        )
        db.add(new_version)
        db.commit()
    return RedirectResponse("/medications/", status_code=303)


@router.post("/{med_id}/stop")
def stop_medication(med_id: int, effective_date: str = Form(""), db: Session = Depends(get_db)):
    med = db.get(Medication, med_id)
    if med:
        med.end_date = date.fromisoformat(effective_date) if effective_date else date.today()
        db.commit()
    return RedirectResponse("/medications/", status_code=303)


@router.post("/{med_id}/delete")
def delete_medication(med_id: int, db: Session = Depends(get_db)):
    med = db.get(Medication, med_id)
    if med:
        db.delete(med)
        db.commit()
    return RedirectResponse("/medications/", status_code=303)
