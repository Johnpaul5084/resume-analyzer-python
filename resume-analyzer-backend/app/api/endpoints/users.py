from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app.api import dependencies as deps
from app.core import security
from app.core.config import settings
from app.db.session import get_db
from app.models.all_models import User
from app.schemas.all_schemas import User, UserCreate, UserUpdate

router = APIRouter()

@router.get("/me", response_model=User)
def read_user_me(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.put("/me", response_model=User)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = UserUpdate(**current_user_data)
    
    if password:
        user_in.password = password
    if full_name:
        user_in.full_name = full_name
    if email:
        user_in.email = email
    
    # Simple update logic
    if password:
        current_user.hashed_password = security.get_password_hash(password)
    
    current_user.full_name = full_name if full_name else current_user.full_name
    current_user.email = email if email else current_user.email
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
