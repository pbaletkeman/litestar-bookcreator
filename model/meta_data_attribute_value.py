from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, List

from advanced_alchemy.base import BigIntAuditBase
from sqlalchemy import String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.meta_data_line import MetaDataLine
# from model.meta_data import MetaData, MetaDataAttributeTag
from model.meta_data_attribute import MetaDataAttribute
# from model.meta_data_tag import MetaDataTag
# from model.meta_data_tag_value import MetaDataTagValue
# from model.meta_data import MetaDataValueCreate

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
    meta_data_line_id: Mapped[int] = mapped_column(ForeignKey(MetaDataLine.id), sort_order=-5)
    attribute_id: Mapped[int] = mapped_column(ForeignKey(MetaDataAttribute.id), sort_order=-5)
    attribute_value: Mapped[Optional[str]] = mapped_column(String(), nullable=True, sort_order=7)

    attribute: Mapped[Optional["MetaDataAttribute"]] = (
        relationship(foreign_keys="[MetaDataAttributeValue.attribute_id]",
                     primaryjoin="MetaDataAttributeValue.attribute_id==MetaDataAttribute.id")
    )

    meta_data_attribute_master_value: Mapped["MetaDataLine"] = (
        relationship(foreign_keys="[MetaDataLine.id]",
                     primaryjoin="MetaDataLine.id==MetaDataAttributeValue.meta_data_line_id")
    )
