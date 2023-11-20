from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from advanced_alchemy.base import BigIntAuditBase
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from shared import BaseModel


class MetaDataTag(BigIntAuditBase):
    """
    <dc:rights>Public domain in the USA.</dc:rights>
    <meta name="cover" content="id-3687803259850171647"/>

    meta_data_tag = dc:rights
    meta_data_tag = meta
    """
    __tablename__ = 'meta_data_tag'
    id: Mapped[int] = mapped_column(primary_key=True, name="meta_data_tag_id", sort_order=-10)
    sort_order: Mapped[int] = mapped_column(nullable=False, default=0, sort_order=1)
    name: Mapped[str] = mapped_column(String(length=30), nullable=False, sort_order=2)
    tag: Mapped[str] = mapped_column(String(length=30), nullable=False, sort_order=3)
    place_holder: Mapped[str] = mapped_column(String(100), nullable=True, sort_order=4)
    tool_tip: Mapped[str] = mapped_column(String(100), nullable=True, sort_order=5)
    description: Mapped[str] = mapped_column(String(), nullable=True, sort_order=6)

    # meta_data_tag_master_value: Mapped[list["MetaDataTagValue"]] = relationship(back_populates="meta_data_tag")

    def __init__(self, **kw: Any):
        super().__init__(**kw)
        if self.sort_order is None:
            self.sort_order = 0


class MetaDataTagDTO(BaseModel):
    id: Optional[int]
    sort_order: Optional[int] = 0
    name: str
    tag: str
    place_holder: Optional[str] = None
    tool_tip: Optional[str] = None
    description: Optional[str] = None


class MetaDataTagCreate(BaseModel):
    name: str
    tag: str
    sort_order: Optional[int] = 0
    place_holder: Optional[str] = None
    tool_tip: Optional[str] = None
    description: Optional[str] = None

