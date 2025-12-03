import uuid
from datetime import datetime
from typing import Annotated, Any, ClassVar

from sqlalchemy import UUID, DateTime, MetaData
from sqlalchemy.orm import DeclarativeBase, mapped_column

POSTGRES_NAMING_CONVENTION = {
    "ix": "%(table_name)s_%(column_0_N_name)s_idx",
    "uq": "%(table_name)s_%(column_0_N_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}


class SAModel(DeclarativeBase):
    __tablename__: str
    metadata = MetaData(naming_convention=POSTGRES_NAMING_CONVENTION)
    type_annotation_map: ClassVar[dict[type, Any]] = {
        datetime: DateTime(timezone=True),
        uuid.UUID: Annotated[
            uuid.UUID,
            mapped_column(UUID, default=uuid.uuid4),
        ],
    }
