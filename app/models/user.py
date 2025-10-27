"""
Modelo de Usuario básico para el sistema MoirAI
Proporciona esquemas de validación y gestión de usuarios
"""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class UserBase(SQLModel):
    """Modelo base del usuario con campos comunes"""
    email: str = Field(unique=True, index=True, max_length=100)
    full_name: str = Field(max_length=100)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    profile_complete: bool = Field(default=False)
    
    # Información académica (estudiantes)
    university: Optional[str] = Field(default=None, max_length=100)
    career: Optional[str] = Field(default=None, max_length=100)
    graduation_year: Optional[int] = None
    
    # Información de contacto
    phone: Optional[str] = Field(default=None, max_length=20)
    linkedin: Optional[str] = Field(default=None, max_length=255)
    github: Optional[str] = Field(default=None, max_length=255)
    portfolio: Optional[str] = Field(default=None, max_length=255)


class User(UserBase, table=True):
    """Modelo de Usuario en la base de datos"""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Password hash (nunca se incluye en respuestas API)
    hashed_password: str = Field(max_length=255)


class UserCreate(UserBase):
    """Esquema para crear un usuario (incluye contraseña)"""
    password: str = Field(min_length=8)


class UserRead(UserBase):
    """Esquema para leer información del usuario (sin información sensible)"""
    id: int
    created_at: datetime
    updated_at: datetime


class UserUpdate(SQLModel):
    """Esquema para actualizar información del usuario"""
    full_name: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    linkedin: Optional[str] = Field(default=None, max_length=255)
    github: Optional[str] = Field(default=None, max_length=255)
    portfolio: Optional[str] = Field(default=None, max_length=255)
    university: Optional[str] = Field(default=None, max_length=100)
    career: Optional[str] = Field(default=None, max_length=100)
    graduation_year: Optional[int] = None
    profile_complete: Optional[bool] = None
