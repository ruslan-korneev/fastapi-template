from typing import Annotated
from uuid import UUID

from asyncpg import UniqueViolationError
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

from src.core.dependencies.containers import Container
from src.core.types.dto import PaginatedResponse
from src.db.session import AsyncSessionMaker
from src.modules.users.dto import UserCreateDTO, UserReadDTO, UserUpdateDTO
from src.modules.users.services import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_user(
    data: UserCreateDTO,
    db_session_maker: Annotated[AsyncSessionMaker, Depends(Provide[Container.db_session_maker])],
) -> UserReadDTO:
    """Create a new user."""
    async with db_session_maker as session:
        service = UserService(session)

        try:
            created_user = await service.create_user(data)
        except IntegrityError as exc:
            await session.rollback()
            cause = exc.orig.__cause__ if exc.orig else None
            if isinstance(cause, UniqueViolationError):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=cause.detail) from exc

            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="internal_error") from exc

        await session.commit()
        return created_user


@router.get("")
@inject
async def get_users(
    db_session_maker: Annotated[AsyncSessionMaker, Depends(Provide[Container.db_session_maker])],
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum number of items to return")] = 20,
    offset: Annotated[int, Query(ge=0, description="Number of items to skip")] = 0,
) -> PaginatedResponse[UserReadDTO]:
    """Get paginated users."""
    async with db_session_maker as session:
        service = UserService(session)
        return await service.get_users_paginated(limit=limit, offset=offset)


@router.get("/{user_id}")
@inject
async def get_user(
    user_id: UUID,
    db_session_maker: Annotated[AsyncSessionMaker, Depends(Provide[Container.db_session_maker])],
) -> UserReadDTO:
    """Get user by ID."""
    async with db_session_maker as session:
        service = UserService(session)
        user = await service.get_user(user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return user


@router.patch("/{user_id}")
@inject
async def update_user(
    user_id: UUID,
    data: UserUpdateDTO,
    db_session_maker: Annotated[AsyncSessionMaker, Depends(Provide[Container.db_session_maker])],
) -> UserReadDTO:
    """Update user by ID."""
    async with db_session_maker as session:
        service = UserService(session)
        user = await service.update_user(user_id, data)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        await session.commit()

        return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_user(
    user_id: UUID,
    db_session_maker: Annotated[AsyncSessionMaker, Depends(Provide[Container.db_session_maker])],
) -> None:
    """Delete user by ID."""
    async with db_session_maker as session:
        service = UserService(session)
        deleted = await service.delete_user(user_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        await session.commit()
