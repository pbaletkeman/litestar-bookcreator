from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, List

from advanced_alchemy.base import BigIntAuditBase
from sqlalchemy import String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.meta_data import MetaData
from model.meta_data_tag import MetaDataTag

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from shared import BaseModel


class MetaDataTagValue(BigIntAuditBase):
    """
    <dc:rights>Public domain in the USA.</dc:rights>
    <meta name="cover" content="id-3687803259850171647"/>
    """
    __tablename__ = 'meta_data_tag_value'
    id: Mapped[int] = mapped_column(primary_key=True, name="meta_data_value_id", sort_order=-10)
    meta_data_id: Mapped[int] = mapped_column(ForeignKey(MetaData.id), sort_order=-5)
    meta_data_tag_id: Mapped[int] = mapped_column(ForeignKey(MetaDataTag.id), sort_order=-5)
    is_empty_tag: Mapped[Optional[bool]] = mapped_column(Boolean(), nullable=True, sort_order=1, default=False)
    tag_value: Mapped[Optional[str]] = mapped_column(String(), nullable=True, sort_order=6)

    meta_data_tags: Mapped[Optional["MetaDataTag"]] = (
        relationship("MetaDataTag", foreign_keys="[MetaDataTagValue.meta_data_tag_id]",)
    )

    meta_data_tag_master_value: Mapped["MetaData"] = (
        relationship(MetaData,  foreign_keys="[MetaData.meta_data_id]",)
    )

    def __init__(self, **kw: Any):
        super().__init__(**kw)
        if self.is_empty_tag is None:
            self.is_empty_tag = False
