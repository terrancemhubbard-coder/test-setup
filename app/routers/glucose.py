from datetime import datetime
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import GlucoseReading
from ..templating import templates

router = APIRouter(prefix="/glucose", tags=["glucose"])

CONTEXTS = ["fasting", "before_meal", "after_meal", "bedtime", "random"]


@router.get("/")
def list_glucose(request: Request, db: Session = Depends(get_db)):
    readings = db.scalars(select(GlucoseReading).order_by(GlucoseReading.timestamp.desc())).all()
    chart_data = [
        {"x": r.timestamp.isoformat(), "y": r.value_mg_dl} for r in reversed(readings)
    ]
    return templates.TemplateResponse(
        "glucose.html",
        {"request": request, "readings": readings, "contexts": CONTEXTS, "chart_data": chart_data},
    )


@router.post("/")
def add_glucose(
    timestamp: str = Form(...),
    value_mg_dl: float = Form(...),
    context: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    db.add(
        GlucoseReading(
            timestamp=datetime.fromisoformat(timestamp),
            value_mg_dl=value_mg_dl,
            context=context or None,
            notes=notes or None,
        )
    )
    db.commit()
    return RedirectResponse("/glucose/", status_code=303)


@router.post("/{reading_id}/delete")
def delete_glucose(reading_id: int, db: Session = Depends(get_db)):
    reading = db.get(GlucoseReading, reading_id)
    if reading:
        db.delete(reading)
        db.commit()
    return RedirectResponse("/glucose/", status_code=303)
