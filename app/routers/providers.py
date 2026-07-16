from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Provider
from ..templating import templates

router = APIRouter(prefix="/providers", tags=["providers"])


@router.get("/")
def list_providers(request: Request, db: Session = Depends(get_db)):
    providers = db.scalars(select(Provider).order_by(Provider.name)).all()
    return templates.TemplateResponse("providers.html", {"request": request, "providers": providers})


@router.post("/")
def add_provider(
    name: str = Form(...),
    specialty: str = Form(""),
    phone: str = Form(""),
    address: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    db.add(
        Provider(
            name=name,
            specialty=specialty or None,
            phone=phone or None,
            address=address or None,
            notes=notes or None,
        )
    )
    db.commit()
    return RedirectResponse("/providers/", status_code=303)


@router.post("/{provider_id}/delete")
def delete_provider(provider_id: int, db: Session = Depends(get_db)):
    provider = db.get(Provider, provider_id)
    if provider:
        db.delete(provider)
        db.commit()
    return RedirectResponse("/providers/", status_code=303)
