from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, List

from advanced_alchemy.base import BigIntAuditBase
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from model.meta_data_attribute import MetaDataAttributeDef
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
    is_empty_tag: Mapped[Optional[bool]] = mapped_column(nullable=False, sort_order=1)
    attribute_id: Mapped[Optional[List[int]]] = mapped_column(ForeignKey(MetaDataAttributeDef.id), sort_order=5)
    tag_value: Mapped[Optional[str]] = mapped_column(String(), nullable=True, sort_order=6)
    attribute_value: Mapped[Optional[str]] = mapped_column(String(), nullable=True, sort_order=7)

    def __init__(self, **kw: Any):
        super().__init__(**kw)
        if self.is_empty_tag is None:
            self.is_empty_tag = False


class MetaDataDefDTO(BaseModel):
    id: Optional[int]
    meta_data_tag_id: int
    is_empty_tag: bool
    attribute_id: Optional[int]
    tag_value: str
    attribute_value: Optional[str]


class MetaDataDefCreate(BaseModel):
    meta_data_tag_id: int
    is_empty_tag: bool
    attribute_id: Optional[int]
    tag_value: str
    attribute_value: Optional[str]


class MetaDataDefUpdate(BaseModel):
    meta_data_tag_id: int
    is_empty_tag: bool
    attribute_id: Optional[int]
    tag_value: str
    attribute_value: Optional[str]
