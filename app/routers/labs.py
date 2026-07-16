from datetime import date
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import LabResult
from ..templating import templates

router = APIRouter(prefix="/labs", tags=["labs"])

COMMON_TESTS = [
    "LDL Cholesterol",
    "HDL Cholesterol",
    "Total Cholesterol",
    "Triglycerides",
    "eGFR",
    "Creatinine",
    "Microalbumin/Creatinine Ratio",
    "Other",
]


@router.get("/")
def list_labs(request: Request, db: Session = Depends(get_db)):
    results = db.scalars(select(LabResult).order_by(LabResult.test_date.desc())).all()

    by_test = {}
    for r in results:
        by_test.setdefault(r.test_name, []).append(r)
    chart_series = {
        name: [{"x": r.test_date.isoformat(), "y": r.value} for r in reversed(entries)]
        for name, entries in by_test.items()
    }

    return templates.TemplateResponse(
        "labs.html",
        {
            "request": request,
            "results": results,
            "common_tests": COMMON_TESTS,
            "chart_series": chart_series,
        },
    )


@router.post("/")
def add_lab(
    test_date: str = Form(...),
    test_name: str = Form(...),
    value: float = Form(...),
    unit: str = Form(""),
    reference_range: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    db.add(
        LabResult(
            test_date=date.fromisoformat(test_date),
            test_name=test_name,
            value=value,
            unit=unit or None,
            reference_range=reference_range or None,
            notes=notes or None,
        )
    )
    db.commit()
    return RedirectResponse("/labs/", status_code=303)


@router.post("/{result_id}/delete")
def delete_lab(result_id: int, db: Session = Depends(get_db)):
    result = db.get(LabResult, result_id)
    if result:
        db.delete(result)
        db.commit()
    return RedirectResponse("/labs/", status_code=303)
