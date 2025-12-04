from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy import func, inspect, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.types.dto import BaseDTO
from src.db.base import SAModel


@dataclass
class PaginatedResult[RDT: BaseDTO]:
    """Result from paginated query."""

    items: Sequence[RDT]
    total: int


class BaseRepository[MT: SAModel, CDT: BaseDTO, RDT: BaseDTO]:
    _model: type[MT]
    _create_dto: type[CDT]
    _read_dto: type[RDT]
    _session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def is_modified(data: MT) -> bool:
        inspr = inspect(data)
        return inspr.modified or not inspr.has_identity

    async def get_all(self) -> Sequence[RDT]:
        query = select(self._model)
        result = await self._session.execute(query)
        return [self._read_dto.model_validate(instance) for instance in result.scalars().all()]

    async def get_paginated(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginatedResult[RDT]:
        """Get paginated records with total count."""
        # Get total count
        count_query = select(func.count()).select_from(self._model)
        total_result = await self._session.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated items
        query = select(self._model).limit(limit).offset(offset)
        result = await self._session.execute(query)
        items = [self._read_dto.model_validate(instance) for instance in result.scalars().all()]

        return PaginatedResult(items=items, total=total)

    async def save(self, data: MT | CDT) -> RDT:
        if not isinstance(data, self._model):
            create_dto = self._create_dto.model_validate(data)
            data = self._model(**create_dto.model_dump())

        elif not self.is_modified(data):
            return self._read_dto.model_validate(data)

        self._session.add(data)
        await self._session.flush()
        await self._session.refresh(data)

        return self._read_dto.model_validate(data)

    async def save_bulk(self, data: Sequence[CDT | MT]) -> None:
        for item in data:
            instance = self._model(**item.model_dump()) if isinstance(item, self._create_dto) else item

            if isinstance(instance, self._model) and self.is_modified(instance):
                self._session.add(instance)

        await self._session.flush()
