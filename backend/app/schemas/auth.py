"""Schémas Pydantic - Auth."""

from datetime import date
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    nom: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-ZÀ-ÿ\s\-]+$",
        description="Nom complet : lettres (accents inclus), espaces et tirets uniquement.",
    )
    email: EmailStr
    password: str
    date_naissance: date


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
