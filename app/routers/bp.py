from datetime import datetime
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import BloodPressureReading
from ..templating import templates

router = APIRouter(prefix="/bp", tags=["bp"])


@router.get("/")
def list_bp(request: Request, db: Session = Depends(get_db)):
    readings = db.scalars(select(BloodPressureReading).order_by(BloodPressureReading.timestamp.desc())).all()
    chart_data = [
        {"x": r.timestamp.isoformat(), "systolic": r.systolic, "diastolic": r.diastolic}
        for r in reversed(readings)
    ]
    return templates.TemplateResponse(
        "bp.html", {"request": request, "readings": readings, "chart_data": chart_data}
    )


@router.post("/")
def add_bp(
    timestamp: str = Form(...),
    systolic: int = Form(...),
    diastolic: int = Form(...),
    pulse: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    db.add(
        BloodPressureReading(
            timestamp=datetime.fromisoformat(timestamp),
            systolic=systolic,
            diastolic=diastolic,
            pulse=int(pulse) if pulse else None,
            notes=notes or None,
        )
    )
    db.commit()
    return RedirectResponse("/bp/", status_code=303)


@router.post("/{reading_id}/delete")
def delete_bp(reading_id: int, db: Session = Depends(get_db)):
    reading = db.get(BloodPressureReading, reading_id)
    if reading:
        db.delete(reading)
        db.commit()
    return RedirectResponse("/bp/", status_code=303)
