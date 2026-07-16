from datetime import date, datetime
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Condition
from ..templating import templates

router = APIRouter(prefix="/conditions", tags=["conditions"])


@router.get("/")
def list_conditions(request: Request, db: Session = Depends(get_db)):
    conditions = db.scalars(select(Condition).order_by(Condition.status, Condition.diagnosed_date.desc())).all()
    return templates.TemplateResponse(
        "conditions.html", {"request": request, "conditions": conditions}
    )


@router.post("/")
def add_condition(
    name: str = Form(...),
    category: str = Form(""),
    diagnosed_date: str = Form(""),
    status: str = Form("active"),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    condition = Condition(
        name=name,
        category=category or None,
        diagnosed_date=date.fromisoformat(diagnosed_date) if diagnosed_date else None,
        status=status,
        notes=notes or None,
    )
    db.add(condition)
    db.commit()
    return RedirectResponse("/conditions/", status_code=303)


@router.post("/{condition_id}/status")
def update_status(condition_id: int, status: str = Form(...), db: Session = Depends(get_db)):
    condition = db.get(Condition, condition_id)
    if condition:
        condition.status = status
        condition.updated_at = datetime.utcnow()
        db.commit()
    return RedirectResponse("/conditions/", status_code=303)


@router.post("/{condition_id}/delete")
def delete_condition(condition_id: int, db: Session = Depends(get_db)):
    condition = db.get(Condition, condition_id)
    if condition:
        db.delete(condition)
        db.commit()
    return RedirectResponse("/conditions/", status_code=303)
