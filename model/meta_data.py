from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, List
from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String
from meta_data_attribute_value import MetaDataAttributeValue
from meta_data_tag_value import MetaDataTagValue

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from shared import BaseModel


class MetaData(BigIntAuditBase):

    __tablename__ = "meta_data_attribute"

    id: Mapped[int] = mapped_column(primary_key=True, name="meta_data_id", sort_order=-10)
    name: Mapped[str] = mapped_column(String(length=30), nullable=False, sort_order=1)

    meta_data_attribute: Mapped[Optional[List["MetaDataAttributeValue"]]] = (
        relationship(back_populates="meta_data_attribute_master_value")
    )
    meta_data_tag: Mapped["MetaDataTagValue"] = relationship(back_populates="meta_data_tag_master_value")
