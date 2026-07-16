from datetime import date
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import PadSymptom
from ..templating import templates

router = APIRouter(prefix="/pad", tags=["pad"])

SYMPTOM_TYPES = [
    "claudication",
    "numbness_tingling",
    "coldness",
    "color_change",
    "wound_ulcer",
    "pulse_check",
    "rest_pain",
    "other",
]


@router.get("/")
def list_pad(request: Request, db: Session = Depends(get_db)):
    entries = db.scalars(select(PadSymptom).order_by(PadSymptom.symptom_date.desc())).all()
    return templates.TemplateResponse(
        "pad.html", {"request": request, "entries": entries, "symptom_types": SYMPTOM_TYPES}
    )


@router.post("/")
def add_pad(
    symptom_date: str = Form(...),
    symptom_type: str = Form(...),
    leg: str = Form(""),
    severity: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    db.add(
        PadSymptom(
            symptom_date=date.fromisoformat(symptom_date),
            symptom_type=symptom_type,
            leg=leg or None,
            severity=severity or None,
            notes=notes or None,
        )
    )
    db.commit()
    return RedirectResponse("/pad/", status_code=303)


@router.post("/{entry_id}/delete")
def delete_pad(entry_id: int, db: Session = Depends(get_db)):
    entry = db.get(PadSymptom, entry_id)
    if entry:
        db.delete(entry)
        db.commit()
    return RedirectResponse("/pad/", status_code=303)
