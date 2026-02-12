"""Authentication API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import SQLModel

from src.api.deps import CurrentUser, DbSession, get_current_user
from src.models.user import (
    NotificationPreferences,
    User,
    UserCreate,
    UserLogin,
    UserPreferencesUpdate,
    UserPublic,
    UserStats,
    UserUpdate,
)
from src.repositories.user_repository import UserRepository
from src.services.auth_service import AuthService
from src.services.task_service import TaskService
from src.services.user_preferences_service import UserPreferencesService

router = APIRouter(prefix="/auth", tags=["auth"])


class TokenResponse(SQLModel):
    """Token response schema."""

    access_token: str
    token_type: str = "bearer"


class MessageResponse(SQLModel):
    """Simple message response."""

    message: str


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, session: DbSession) -> User:
    """Register a new user."""
    auth_service = AuthService(session)
    try:
        user = await auth_service.register(email=user_data.email, password=user_data.password)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, session: DbSession) -> TokenResponse:
    """Login and get access token."""
    auth_service = AuthService(session)
    user = await auth_service.authenticate(email=credentials.email, password=credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    token = AuthService.create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserPublic)
async def get_current_user_info(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """Get current authenticated user."""
    return current_user


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: Annotated[User, Depends(get_current_user)]) -> MessageResponse:
    """Logout current user.

    Note: With JWT tokens, the actual invalidation happens client-side
    by removing the token. This endpoint exists for API completeness
    and could be extended for token blacklisting if needed.
    """
    return MessageResponse(message="Successfully logged out")


@router.patch("/me", response_model=UserPublic)
async def update_profile(
    user_data: UserUpdate, session: DbSession, current_user: CurrentUser
) -> User:
    """Update current user's profile."""
    user_repo = UserRepository(session)
    updated_user = await user_repo.update(
        user=current_user,
        display_name=user_data.display_name,
    )
    return updated_user


@router.get("/me/stats", response_model=UserStats)
async def get_user_stats(session: DbSession, current_user: CurrentUser) -> UserStats:
    """Get current user's task statistics."""
    task_service = TaskService(session)
    stats = await task_service.get_user_stats(current_user.id)
    return UserStats(**stats)


@router.get("/me/preferences", response_model=NotificationPreferences)
async def get_preferences(
    session: DbSession, current_user: CurrentUser
) -> NotificationPreferences:
    """Get current user's notification preferences."""
    prefs_service = UserPreferencesService(session)
    return await prefs_service.get_preferences(current_user.id)


@router.patch("/me/preferences", response_model=NotificationPreferences)
async def update_preferences(
    updates: UserPreferencesUpdate,
    session: DbSession,
    current_user: CurrentUser,
) -> NotificationPreferences:
    """Update current user's notification preferences."""
    prefs_service = UserPreferencesService(session)
    return await prefs_service.update_preferences(current_user.id, updates)
