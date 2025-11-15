from fastapi import APIRouter, Path, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from users.schemas import *
from users.models import UserModel, TokenModel, UserType
from sqlalchemy.orm import Session
from core.database import get_db
from typing import List
import secrets
from auth.jwt_auth import (
    generate_access_token,
    generate_refresh_token,
    decode_refresh_token,
    get_authenticated_admin,
)

router = APIRouter(tags=["users"], prefix="/users")


def generate_token(length=32):
    return secrets.token_hex(length)


@router.post("/login")
async def user_login(request: UserLoginSchema, db: Session = Depends(get_db)):
    user_obj = (
        db.query(UserModel)
        .filter_by(username=request.username.lower())
        .first()
    )
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username doesnt exists",
        )
    if not user_obj.verify_password(request.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="password is invalid",
        )

    # Token Based Authentication
    # token_obj = TokenModel(user_id=user_obj.id, token=generate_token())
    # db.add(token_obj)
    # db.commit()
    # db.refresh(token_obj)

    access_token = generate_access_token(user_obj.id)
    refresh_token = generate_refresh_token(user_obj.id)
    return JSONResponse(
        content={
            "detail": "logged in successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    )


@router.post("/register")
async def user_login(
    request: UserRegisterSchema, db: Session = Depends(get_db)
):
    if (
        db.query(UserModel)
        .filter_by(username=request.username.lower())
        .first()
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="username already exists",
        )
    user_obj = UserModel(
        username=request.username.lower(), user_type=UserType.USER
    )
    user_obj.set_password(request.password)
    db.add(user_obj)
    db.commit()
    return JSONResponse(content={"detail": "user registered successfully"})


@router.post("/refresh-token")
async def user_refresh_token(
    request: UserRefreshTokenSchema, db: Session = Depends(get_db)
):
    user_id = decode_refresh_token(request.token)
    access_token = generate_access_token(user_id)
    return JSONResponse(content={"access_token": access_token})


@router.get("/admin_dashboard")
def admin_dashboard(user: UserModel = Depends(get_authenticated_admin)):
    return {
        "message": "Welcome to the admin dashboard!",
        "admin": user.username,
    }
