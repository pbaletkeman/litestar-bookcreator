from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from model.base import BaseModel, Base


class MetaDataLine(Base):
    __tablename__ = 'meta_data_line'

    id: Mapped[int] = mapped_column(primary_key=True, name='line_id', sort_order=-10)
    name: Mapped[str] = mapped_column(String(length=30), nullable=False, sort_order=1)
    attributes: Mapped[List['MetaDataAttributeValue']] = (
        relationship('MetaDataAttributeValue', back_populates='meta_data_attribute_master_value',)
    )
    tag: Mapped['MetaDataTagValue'] = (
        relationship('MetaDataTagValue', back_populates='meta_data_tag_master_value',)
    )


class MetaDataTagValueDTO(BaseModel):
    id: int | None
    tag_id: int
    value: str | None


class MetaDataValueCreate(BaseModel):
    tag_id: int
    value: str | None


class MetaDataAttributeValueDTO(BaseModel):
    id: int | None
    attributes: List[MetaDataAttributeTag] | None


class MetaDataAttributeValueCreate(BaseModel):
    attributes: List[MetaDataAttributeTag] | None


class MetaDataAttributeTag(BaseModel):
    id: int
    value: str


class MetaDataLineDTO(BaseModel):
    id: Optional[int]
    name: str
    tag: MetaDataTagValueDTO
    attributes: List[MetaDataAttributeTag] | None


class MetaDataLineCreate(BaseModel):
    name: str
    tag: MetaDataValueCreate
    attributes: List[MetaDataAttributeTag] | None
