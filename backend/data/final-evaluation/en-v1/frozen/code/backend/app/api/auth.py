from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, Response
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, ConfigDict, Field, StrictBool
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.models.models import User
from app.services.access import Role
from app.services.auth import create_access_token
from app.services.users import UserService
from app.settings import settings

router = APIRouter()


@router.get("/auth/config")
async def registration_config():
    return {"allowed_email_domain": settings.ALLOWED_EMAIL_DOMAIN.lower()}


class AssigneeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str


@router.get("/admin/assignees", response_model=list[AssigneeResponse])
async def assignees(limit: Annotated[int, Query(ge=1, le=100)] = 100,
                    offset: Annotated[int, Query(ge=0)] = 0,
                    actor: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await UserService(db).assignees(actor, limit=limit, offset=offset)


class Registration(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str = Field(max_length=254)
    password: str = Field(min_length=12, max_length=128, repr=False)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    role: Role | None
    is_approved: bool
    is_active: bool
    approved_at: datetime | None
    approved_by_id: int | None
    created_at: datetime
    updated_at: datetime


class RoleUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: Role


class ActiveUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    is_active: StrictBool


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int


@router.post("/auth/register", response_model=UserResponse, status_code=201)
async def register(body: Registration, db: AsyncSession = Depends(get_db)):
    return await UserService(db).register(body.email, body.password)


@router.post("/auth/token", response_model=TokenResponse)
async def login(response: Response, form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await UserService(db).login(form.username, form.password)
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return TokenResponse(access_token=create_access_token(user.id), expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)


@router.get("/users/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)):
    return user


@router.get("/admin/users", response_model=list[UserResponse])
async def users(pending: bool | None = None, limit: Annotated[int, Query(ge=1, le=100)] = 20,
                offset: Annotated[int, Query(ge=0)] = 0,
                actor: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await UserService(db).list_users(actor, pending=pending, limit=limit, offset=offset)


@router.post("/admin/users/{user_id}/approve", response_model=UserResponse)
async def approve(user_id: int, body: RoleUpdate, actor: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await UserService(db).approve(actor, user_id, body.role)


@router.patch("/admin/users/{user_id}/role", response_model=UserResponse)
async def role(user_id: int, body: RoleUpdate, actor: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await UserService(db).change_role(actor, user_id, body.role)


@router.patch("/admin/users/{user_id}/active", response_model=UserResponse)
async def active(user_id: int, body: ActiveUpdate, actor: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await UserService(db).set_active(actor, user_id, body.is_active)
