from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional
from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from shared import BaseModel

0


class MetaDataAttributeDef(BigIntAuditBase):
    """
    <meta property="role" refines="#author_0" scheme="marc:relators">aut</meta>
    Attribute = property
    Attribute = refines
    Attribute = scheme
    """
    __tablename__ = "meta_data_attribute_def"

    id: Mapped[int] = mapped_column(primary_key=True, name="attribute_id", sort_order=-10)
    sort_order: Mapped[int | None] = mapped_column(nullable=False, default=0, sort_order=0)
    name: Mapped[str] = mapped_column(String(length=30), nullable=False, sort_order=1)
    place_holder: Mapped[str] = mapped_column(String(100), nullable=True, sort_order=3)
    tool_tip: Mapped[str] = mapped_column(String(100), nullable=True, sort_order=4)
    description: Mapped[str] = mapped_column(String(), nullable=True, sort_order=5)

    meta_data_attribute: Mapped[Optional[list["MetaDataDef"]]] = relationship(back_populates="attributes")

    def __init__(self, **kw: Any):
        super().__init__(**kw)
        if self.sort_order is None:
            self.sort_order = 0


class MetaDataAttributeDefDTO(BaseModel):
    id: int | None
    sort_order: Optional[int] = 0
    name: str
    place_holder: Optional[str] = None
    tool_tip: Optional[str] = None
    description: Optional[str] = None


class MetaDataAttributeDefCreate(BaseModel):
    name: str
    sort_order: Optional[int] = 0
    place_holder: Optional[str] = None
    tool_tip: Optional[str] = None
    description: Optional[str] = None


class MetaDataAttributeTag(BaseModel):
    id: int
    value: str
