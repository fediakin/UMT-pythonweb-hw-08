from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactResponse, ContactUpdate

router = APIRouter(prefix="/contacts", tags=["Contacts"])

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(contact_data: ContactCreate, db: Session = Depends(get_db)):
    stmt = select(Contact).where(Contact.email == contact_data.email)
    existing_contact = db.scalars(stmt).first()
    if existing_contact:
        raise HTTPException(status_code=409, detail="Email is already in use")

    new_contact = Contact(**contact_data.model_dump())
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact

@router.get("/", response_model=List[ContactResponse])
def get_contacts(
    first_name: str | None = Query(default=None),
    last_name: str | None = Query(default=None),
    email: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(Contact)

    filters = []
    if first_name:
        filters.append(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        filters.append(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        filters.append(Contact.email.ilike(f"%{email}%"))

    if filters:
        stmt = stmt.where(or_(*filters))

    contacts = db.scalars(stmt).all()
    return contacts

@router.get("/birthdays", response_model=List[ContactResponse])
def get_upcoming_birthdays(db: Session = Depends(get_db)):
    stmt = select(Contact)
    all_contacts = db.scalars(stmt).all()
    today = date.today()
    upcoming = []

    for contact in all_contacts:
        try:
            bday_this_year = contact.birthday.replace(year=today.year)
        except ValueError:
            bday_this_year = date(today.year, 3, 1)

        if bday_this_year < today:
            try:
                bday_this_year = contact.birthday.replace(year=today.year + 1)
            except ValueError:
                bday_this_year = date(today.year + 1, 3, 1)

        if 0 <= (bday_this_year - today).days <= 7:
            upcoming.append(contact)

    return upcoming

@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    stmt = select(Contact).where(Contact.id == contact_id)
    contact = db.scalars(stmt).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(contact_id: int, contact_data: ContactUpdate, db: Session = Depends(get_db)):
    stmt = select(Contact).where(Contact.id == contact_id)
    contact = db.scalars(stmt).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    if contact_data.email != contact.email:
        email_stmt = select(Contact).where(Contact.email == contact_data.email)
        if db.scalars(email_stmt).first():
            raise HTTPException(status_code=409, detail="Email is already in use")

    for key, value in contact_data.model_dump().items():
        setattr(contact, key, value)

    db.commit()
    db.refresh(contact)
    return contact

@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    stmt = select(Contact).where(Contact.id == contact_id)
    contact = db.scalars(stmt).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(contact)
    db.commit()