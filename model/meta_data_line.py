from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, List, Union
from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from shared import BaseModel


class MetaDataLine(BigIntAuditBase):
    __tablename__ = "meta_data_line"

    id: Mapped[int] = mapped_column(primary_key=True, name="line_id", sort_order=-10)
    name: Mapped[str] = mapped_column(String(length=30), nullable=False, sort_order=1)
    # meta_data_tag: Mapped[List["MetaDataTagValue"]] = relationship(back_populates="meta_data_tag_master_value")


class MetaDataTagValueDTO(BaseModel):
    id: int | None
    tag_id: int
    value: Union[str | None]


class MetaDataValueCreate(BaseModel):
    tag_id: int
    value: str | None


class MetaDataAttributeValueDTO(BaseModel):
    id: int | None
    attributes: list[MetaDataAttributeTag] | None


class MetaDataAttributeValueCreate(BaseModel):
    attributes: list[MetaDataAttributeTag] | None


class MetaDataAttributeTag(BaseModel):
    id: int
    value: str


class MetaDataLineDTO(BaseModel):
    id: Optional[int]
    name: str
    meta_data_tag_value: MetaDataTagValueDTO
    meta_data_attribute_value: MetaDataAttributeValueDTO | None


class MetaDataLineCreate(BaseModel):
    name: str
    meta_data_tag_value: MetaDataValueCreate
    meta_data_attribute_value_create: MetaDataAttributeValueCreate | None
