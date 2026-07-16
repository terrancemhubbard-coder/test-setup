from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import Session
from pathlib import Path

from .database import init_db, get_db
from .templating import templates
from .models import (
    Condition,
    Medication,
    Allergy,
    GlucoseReading,
    A1cResult,
    BloodPressureReading,
    PadSymptom,
    LabResult,
)
from .routers import conditions, medications, allergies, providers, glucose, a1c, bp, pad, labs

app = FastAPI(title="Health History")

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(conditions.router)
app.include_router(medications.router)
app.include_router(allergies.router)
app.include_router(providers.router)
app.include_router(glucose.router)
app.include_router(a1c.router)
app.include_router(bp.router)
app.include_router(pad.router)
app.include_router(labs.router)


@app.get("/")
def dashboard(request: Request, db: Session = Depends(get_db)):
    active_conditions = db.scalars(
        select(Condition).where(Condition.status == "active").order_by(Condition.diagnosed_date.desc())
    ).all()
    active_meds = db.scalars(
        select(Medication).where(Medication.end_date.is_(None)).order_by(Medication.name)
    ).all()
    allergies_list = db.scalars(select(Allergy)).all()

    recent_glucose = db.scalars(
        select(GlucoseReading).order_by(GlucoseReading.timestamp.desc()).limit(14)
    ).all()
    glucose_chart = [{"x": r.timestamp.isoformat(), "y": r.value_mg_dl} for r in reversed(recent_glucose)]

    recent_bp = db.scalars(
        select(BloodPressureReading).order_by(BloodPressureReading.timestamp.desc()).limit(14)
    ).all()
    bp_chart = [
        {"x": r.timestamp.isoformat(), "systolic": r.systolic, "diastolic": r.diastolic}
        for r in reversed(recent_bp)
    ]

    recent_a1c = db.scalars(select(A1cResult).order_by(A1cResult.test_date.desc()).limit(8)).all()
    a1c_chart = [{"x": r.test_date.isoformat(), "y": r.value_percent} for r in reversed(recent_a1c)]

    recent_pad = db.scalars(select(PadSymptom).order_by(PadSymptom.symptom_date.desc()).limit(5)).all()

    latest_labs = {}
    for r in db.scalars(select(LabResult).order_by(LabResult.test_date.desc())).all():
        latest_labs.setdefault(r.test_name, r)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "active_conditions": active_conditions,
            "active_meds": active_meds,
            "allergies": allergies_list,
            "latest_glucose": recent_glucose[0] if recent_glucose else None,
            "glucose_chart": glucose_chart,
            "latest_bp": recent_bp[0] if recent_bp else None,
            "bp_chart": bp_chart,
            "latest_a1c": recent_a1c[0] if recent_a1c else None,
            "a1c_chart": a1c_chart,
            "recent_pad": recent_pad,
            "latest_labs": latest_labs,
        },
    )
