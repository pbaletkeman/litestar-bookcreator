from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, List
from litestar.contrib.sqlalchemy.base import BigIntAuditBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from shared import SlugKey, BaseModel
from logger import logger


# The `AuditBase` class includes the same UUID` based primary key (`id`) and 2
# additional columns: `created` and `updated`. `created` is a timestamp of when the
# record created, and `updated` is the last time the record was modified.
class MetaData(BigIntAuditBase):
    """
    <meta property="dcterms:modified">2023-10-01T07:32:26Z</meta>
    tag = meta
    attribute = property
    attribute_value = dcterms:modified
    meta_data_value = 2023-10-01T07:32:26Z
    """
    __tablename__ = 'meta_data'
    id: Mapped[int] = mapped_column(primary_key=True, name="meta_data_id", sort_order=-10)

    meta_data_tag_id: Mapped[int] = mapped_column(ForeignKey("meta_data_tag.meta_data_tag_id"), sort_order=-5)
    attribute_id: Mapped[int] = mapped_column(ForeignKey("attribute.attribute_id"), sort_order=-5)

    meta_data_value: Mapped[str] = mapped_column(String(), nullable=True, sort_order=4)
    attribute_value: Mapped[str] = mapped_column(String(), nullable=True, sort_order=4)


class MetaDataTag(BigIntAuditBase, SlugKey):
    """
    <dc:rights>Public domain in the USA.</dc:rights>
    <meta name="cover" content="id-3687803259850171647"/>

    meta_data_tag = dc:rights
    meta_data_tag = meta
    """
    __tablename__ = 'meta_data_tag'
    id: Mapped[int] = mapped_column(primary_key=True, name="meta_data_tag_id", sort_order=-10)
    is_empty_tag: Mapped[bool | None] = mapped_column(default=False, sort_order=0)
    sort_order: Mapped[int] = mapped_column(nullable=False, default=0, sort_order=1)
    name: Mapped[str] = mapped_column(String(length=30), nullable=False, sort_order=2)
    tag: Mapped[str] = mapped_column(String(length=30), nullable=False, sort_order=3)
    description: Mapped[str] = mapped_column(String(), nullable=True, sort_order=4)

    attribute: Mapped[List["Attribute"]] = relationship(back_populates="item_tag")

    def __init__(self, **kw: Any):
        super().__init__(**kw)
        if self.is_empty_tag is None:
            self.is_empty_tag = False
        if self.sort_order is None:
            self.sort_order = 0


class MetaDataTagDTO(BaseModel):
    id: Optional[int]
    sort_order: Optional[int] = 0
    slug: str
    name: str
    tag: str
    is_empty_tag: Optional[bool] = False
    description: Optional[str] = None


class MetaDataTagCreate(BaseModel):
    name: str
    tag: str
    is_empty_tag: Optional[bool] = False
    sort_order: Optional[int] = 0
    description: Optional[str] = None


class MetaDataTagUpdate(BaseModel):
    sort_order: Optional[int] = 0
    name: str
    tag: str
    is_empty_tag: Optional[bool] = False
    description: Optional[str] = None


class Attribute(BigIntAuditBase):
    """
    <meta property="role" refines="#author_0" scheme="marc:relators">aut</meta>
    Attribute = property
    Attribute = refines
    Attribute = scheme
    """
    __tablename__ = "attribute"

    id: Mapped[int] = mapped_column(primary_key=True, name="attribute_id", sort_order=-10)
    meta_data_tag_id: Mapped[int] = mapped_column(ForeignKey("meta_data_tag.meta_data_tag_id"), sort_order=-5)
    sort_order: Mapped[int | None] = mapped_column(nullable=False, default=0, sort_order=0)
    name: Mapped[str] = mapped_column(String(length=30), nullable=False, sort_order=1)
    description: Mapped[str] = mapped_column(String(), nullable=True, sort_order=2)

    item_tag: Mapped["MetaDataTag"] = relationship(back_populates="attributes", lazy="selectin")

    def __init__(self, **kw: Any):
        super().__init__(**kw)
        if self.sort_order is None:
            self.sort_order = 0


class AttributeDTO(BaseModel):
    id: int | None
    sort_order: Optional[int] = 0
    name: str
    description: Optional[str] = None
    meta_data_tag_id: int


class AttributeCreate(BaseModel):
    name: str
    sort_order: Optional[int] = 0
    description: Optional[str] = None


class AttributeUpdate(BaseModel):
    name: str
    sort_order: Optional[int] = 0
    description: Optional[str] = None
