from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, List

from advanced_alchemy.base import BigIntAuditBase
from sqlalchemy import String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.meta_data import MetaData
from model.meta_data_attribute import MetaDataAttribute
from model.meta_data_tag import MetaDataTag
from model.meta_data_tag_value import MetaDataTagValue, MetaDataValueCreate

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from shared import BaseModel


class MetaDataAttributeValue(BigIntAuditBase):
    """
    <dc:rights>Public domain in the USA.</dc:rights>
    <meta name="cover" content="id-3687803259850171647"/>
    """
    __tablename__ = 'meta_data_attribute_value'
    id: Mapped[int] = mapped_column(primary_key=True, name="meta_data_attribute_value_id", sort_order=-10)
    meta_data_id: Mapped[int] = mapped_column(ForeignKey(MetaData.id), sort_order=-5)
    attributes_id: Mapped[int] = mapped_column(ForeignKey(MetaDataAttribute.id), sort_order=-5)
    attribute_value: Mapped[Optional[str]] = mapped_column(String(), nullable=True, sort_order=7)
    attribute: Mapped[Optional["MetaDataAttribute"]] = relationship(back_populates="meta_data_attribute_value",
                                                                    lazy='noload')
    meta_data_attribute_master_value: Mapped[Optional["MetaData"]] = relationship(back_populates="meta_data_attribute",
                                                                                  lazy='noload')


class MetaDataAttributeValueDTO(BaseModel):
    id: int | None
    attributes: list[MetaDataAttributeTag] | None


class MetaDataAttributeValueCreate(BaseModel):
    meta_data_tag_id: int
    attributes: list[MetaDataAttributeTag] | None


class MetaDataAttributeTag(BaseModel):
    id: int
    value: str


"""
{
  "meta_data_tag_id": 3,
  "tag_value": "string",
  "attributes": [
    {"id":1,"value":"test"}
  ]
}
"""
