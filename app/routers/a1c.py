from datetime import date
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import A1cResult
from ..templating import templates

router = APIRouter(prefix="/a1c", tags=["a1c"])


@router.get("/")
def list_a1c(request: Request, db: Session = Depends(get_db)):
    results = db.scalars(select(A1cResult).order_by(A1cResult.test_date.desc())).all()
    chart_data = [{"x": r.test_date.isoformat(), "y": r.value_percent} for r in reversed(results)]
    return templates.TemplateResponse(
        "a1c.html", {"request": request, "results": results, "chart_data": chart_data}
    )


@router.post("/")
def add_a1c(
    test_date: str = Form(...),
    value_percent: float = Form(...),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    db.add(A1cResult(test_date=date.fromisoformat(test_date), value_percent=value_percent, notes=notes or None))
    db.commit()
    return RedirectResponse("/a1c/", status_code=303)


@router.post("/{result_id}/delete")
def delete_a1c(result_id: int, db: Session = Depends(get_db)):
    result = db.get(A1cResult, result_id)
    if result:
        db.delete(result)
        db.commit()
    return RedirectResponse("/a1c/", status_code=303)
