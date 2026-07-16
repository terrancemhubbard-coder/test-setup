from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Allergy
from ..templating import templates

router = APIRouter(prefix="/allergies", tags=["allergies"])


@router.get("/")
def list_allergies(request: Request, db: Session = Depends(get_db)):
    allergies = db.scalars(select(Allergy).order_by(Allergy.allergen)).all()
    return templates.TemplateResponse("allergies.html", {"request": request, "allergies": allergies})


@router.post("/")
def add_allergy(
    allergen: str = Form(...),
    reaction: str = Form(""),
    severity: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    db.add(Allergy(allergen=allergen, reaction=reaction or None, severity=severity or None, notes=notes or None))
    db.commit()
    return RedirectResponse("/allergies/", status_code=303)


@router.post("/{allergy_id}/delete")
def delete_allergy(allergy_id: int, db: Session = Depends(get_db)):
    allergy = db.get(Allergy, allergy_id)
    if allergy:
        db.delete(allergy)
        db.commit()
    return RedirectResponse("/allergies/", status_code=303)
