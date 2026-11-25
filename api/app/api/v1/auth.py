from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserPublic
from app.services.auth_service import (
    EmailTakenError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidRefreshError,
    SessionResult,
    UnderAgeError,
    login_user,
    logout_user,
    refresh_session,
    register_user,
)

REFRESH_COOKIE = "refresh_token"

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(
    body: RegisterRequest,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    try:
        result = register_user(db, body)
    except UnderAgeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except EmailTakenError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    _set_refresh_cookie(response, result.refresh_token)
    return _token_response(result)


@router.post("/login", response_model=TokenResponse)
def login(
    body: LoginRequest,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    try:
        result = login_user(db, body)
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except InactiveUserError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    _set_refresh_cookie(response, result.refresh_token)
    return _token_response(result)


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> TokenResponse:
    try:
        result = refresh_session(db, refresh_token)
    except InvalidRefreshError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    _set_refresh_cookie(response, result.refresh_token)
    return _token_response(result)


@router.post("/logout", status_code=204)
def logout(
    db: Annotated[Session, Depends(get_db)],
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> Response:
    logout_user(db, refresh_token)
    response = Response(status_code=204)
    _clear_refresh_cookie(response)
    return response


@router.get("/me", response_model=UserPublic)
def me(user: Annotated[User, Depends(get_current_user)]) -> User:
    return user


def _token_response(result: SessionResult) -> TokenResponse:
    return TokenResponse(
        access_token=result.access_token,
        token_type="bearer",
        user=UserPublic.model_validate(result.user),
    )


def _set_refresh_cookie(response: Response, raw_token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=raw_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )


def _clear_refresh_cookie(response: Response) -> None:
    settings = get_settings()
    response.delete_cookie(
        key=REFRESH_COOKIE,
        path="/",
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
    )
