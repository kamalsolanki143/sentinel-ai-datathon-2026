"""
Sentinel AI - Authentication Router
File: backend/api/auth.py
Purpose: Provides registration and login API endpoints for law enforcement officers.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.database.postgres import get_db
from backend.database.models import Officer, OfficerRole
from backend.auth.auth_handler import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterInput(BaseModel):
    name: str = Field(..., description="Full name of the officer")
    badge_number: str = Field(..., description="Unique badge number")
    rank: str = Field(..., description="Officer rank")
    department: str = Field(..., description="Department name")
    password: str = Field(..., description="Plaintext password")
    role: str = Field("officer", description="Officer role (officer, admin, analyst)")


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_officer(
    payload: RegisterInput,
    db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    """Register a new law enforcement officer."""
    existing_q = select(Officer).where(Officer.badge_number == payload.badge_number)
    res = await db.execute(existing_q)
    if res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Officer with this badge number is already registered."
        )

    role_val = OfficerRole.officer
    if payload.role.lower() == "admin":
        role_val = OfficerRole.admin
    elif payload.role.lower() == "analyst":
        role_val = OfficerRole.analyst

    hashed = hash_password(payload.password)
    new_officer = Officer(
        name=payload.name,
        badge_number=payload.badge_number,
        rank=payload.rank,
        department=payload.department,
        hashed_password=hashed,
        role=role_val
    )
    db.add(new_officer)
    await db.commit()
    await db.refresh(new_officer)

    return {
        "id": str(new_officer.id),
        "name": new_officer.name,
        "badge_number": new_officer.badge_number,
        "role": new_officer.role.value
    }


@router.post("/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    """Authenticate officer credentials and return JWT bearer token. (Username maps to badge number)"""
    query = select(Officer).where(Officer.badge_number == form_data.username)
    result = await db.execute(query)
    officer = result.scalar_one_or_none()
    if not officer or not verify_password(form_data.password, officer.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid badge number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = {
        "sub": str(officer.id),
        "name": officer.name,
        "badge_number": officer.badge_number,
        "role": officer.role.value
    }
    access_token = create_access_token(data=token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "officer": {
            "id": str(officer.id),
            "name": officer.name,
            "badge_number": officer.badge_number,
            "role": officer.role.value
        }
    }
