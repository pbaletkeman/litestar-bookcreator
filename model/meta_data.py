from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, List

from advanced_alchemy.base import BigIntAuditBase
from sqlalchemy import String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.meta_data_attribute import MetaDataAttributeDef, MetaDataAttributeTag
from model.meta_data_tag import MetaDataTagDef

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from shared import BaseModel


class MetaDataDef(BigIntAuditBase):
    """
    <dc:rights>Public domain in the USA.</dc:rights>
    <meta name="cover" content="id-3687803259850171647"/>
    """
    __tablename__ = 'meta_data_def'
    id: Mapped[int] = mapped_column(primary_key=True, name="meta_data_id", sort_order=-10)
    meta_data_tag_id: Mapped[int] = mapped_column(ForeignKey(MetaDataTagDef.id), sort_order=-5)
    is_empty_tag: Mapped[Optional[bool]] = mapped_column(Boolean(), nullable=True, sort_order=1, default=False)
    attribute_id: Mapped[Optional[List[int]]] = mapped_column(ForeignKey(MetaDataAttributeDef.id), sort_order=5)
    tag_value: Mapped[Optional[str]] = mapped_column(String(), nullable=True, sort_order=6)
    attribute_value: Mapped[Optional[str]] = mapped_column(String(), nullable=True, sort_order=7)

    attributes: Mapped[Optional["MetaDataAttributeDef"]] = relationship(back_populates="meta_data_attribute",
                                                                        lazy='noload')

    def __init__(self, **kw: Any):
        super().__init__(**kw)
        if self.is_empty_tag is None:
            self.is_empty_tag = False


class MetaDataDefDTO(BaseModel):
    id: int | None
    meta_data_tag_id: int
    is_empty_tag: bool | None = False
    tag_value: str
    attributes: list[MetaDataAttributeTag] | None


class MetaDataDefCreate(BaseModel):
    meta_data_tag_id: int
    tag_value: str
    is_empty_tag: bool | None = False
    attributes: list[MetaDataAttributeTag] | None


class MetaDataDefUpdate(BaseModel):
    meta_data_tag_id: int
    tag_value: str
    is_empty_tag: bool | None = False
    attributes: list[MetaDataAttributeTag] | None

"""
{
  "meta_data_tag_id": 3,
  "tag_value": "string",
  "attributes": [
    {"id":1,"value":"test"}
  ]
}
"""