from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, List
from uuid import UUID

from litestar import HttpMethod
from litestar import route
from litestar.pagination import OffsetPagination
from pydantic import TypeAdapter
from sqlalchemy import ForeignKey
from sqlalchemy.types import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from litestar import Controller
from litestar import get, post, delete
from litestar.contrib.sqlalchemy.base import UUIDAuditBase
from litestar.di import Provide
from litestar.params import Parameter
from litestar.repository.filters import LimitOffset

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from shared import SlugKey, SQLAlchemyAsyncSlugRepository, BaseModel


# The `AuditBase` class includes the same UUID` based primary key (`id`) and 2
# additional columns: `created` and `updated`. `created` is a timestamp of when the
# record created, and `updated` is the last time the record was modified.
class MetaDataTag(UUIDAuditBase, SlugKey):
    """
    <dc:rights>Public domain in the USA.</dc:rights>
    <meta property="role" refines="#author_0" scheme="marc:relators">aut</meta>
    MetaDataTag can have zero or more attributes
    """
    __tablename__ = 'meta_data_tag'

    is_empty_tag: Mapped[bool | None] = mapped_column(default=False)
    sort_order: Mapped[int] = mapped_column(nullable=False, default=0)
    name: Mapped[str] = mapped_column(String(length=30), nullable=False)
    tag: Mapped[str] = mapped_column(String(length=30), nullable=False)
    description: Mapped[str | None]

    attributes: Mapped[List["Attribute"]] = relationship(back_populates="item_tag")

    def __init__(self, **kw: Any):
        super().__init__(**kw)
        if self.is_empty_tag is None:
            self.is_empty_tag = False
        if self.sort_order is None:
            self.sort_order = 0


class Attribute(UUIDAuditBase):
    __tablename__ = "attribute"

    id: Mapped[int] = mapped_column(primary_key=True)
    sort_order: Mapped[int | None] = mapped_column(nullable=False, default=0)  # = mapped_column("sortOrder")
    name: Mapped[str] = mapped_column(String(length=30), nullable=False)

    meta_data_tag_id: Mapped[UUID] = mapped_column(ForeignKey("meta_data_tag.id"))
    item_tag: Mapped["MetaDataTag"] = relationship(back_populates="attributes", lazy="selectin")

    def __init__(self, **kw: Any):
        super().__init__(**kw)
        if self.sort_order is None:
            self.sort_order = 0


class MetaDataTagRepository(SQLAlchemyAsyncSlugRepository[MetaDataTag]):
    """Blog Post repository."""

    model_type = MetaDataTag


class MetaDataTagDTO(BaseModel):
    id: UUID | None
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


# we can optionally override the default `select` used for the repository to pass in
# specific SQL options such as join details
async def provide_meta_data_tag_repo(db_session: AsyncSession) -> MetaDataTagRepository:
    """This provides a simple example demonstrating how to override the join options
    for the repository."""
    return MetaDataTagRepository(session=db_session)


class MetaDataTagController(Controller):
    path = '/meta-data-tag'
    controller_tag = ['Meta Data']

    dependencies = {"meta_data_tag_repo": Provide(provide_meta_data_tag_repo)}

    @get(path='/', tags=controller_tag)
    async def list_items(
            self,
            meta_data_tag_repo: MetaDataTagRepository,
            limit_offset: LimitOffset,
    ) -> OffsetPagination[MetaDataTagDTO]:
        """List items."""
        results, total = await meta_data_tag_repo.list_and_count(limit_offset)
        type_adapter = TypeAdapter(list[MetaDataTagDTO])
        return OffsetPagination[MetaDataTagDTO](
            items=type_adapter.validate_python(results),
            total=total,
            limit=limit_offset.limit,
            offset=limit_offset.offset,
        )

    @get(path="/{item_slug:str}", tags=controller_tag)
    async def get_item_details(self, item_slug: str, meta_data_tag_repo: MetaDataTagRepository, ) -> MetaDataTagDTO:
        """Interact with SQLAlchemy engine and session."""
        obj = await meta_data_tag_repo.get_one(slug=item_slug)
        return MetaDataTagDTO.model_validate(obj)

    @post(path="/", tags=controller_tag)
    async def create_item(self, meta_data_tag_repo: MetaDataTagRepository, data: MetaDataTagCreate, ) -> MetaDataTagDTO:
        """Create a new meta_data tag."""
        _data = data.model_dump(exclude_unset=True, by_alias=False, exclude_none=True)
        _data["slug"] = await meta_data_tag_repo.get_available_slug(_data["name"])
        obj = await meta_data_tag_repo.add(MetaDataTag(**_data))
        await meta_data_tag_repo.session.commit()
        return MetaDataTagDTO.model_validate(obj)

    @route(path="/{id:uuid}", http_method=[HttpMethod.PUT, HttpMethod.PATCH], tags=controller_tag)
    async def update_item(
            self,
            meta_data_tag_repo: MetaDataTagRepository,
            data: MetaDataTagUpdate,
            id: UUID = Parameter(title="MetaData.py ID", description="The meta_data to update.", ),
    ) -> MetaDataTagUpdate:
        """Update an meta_data tag."""
        raw_obj = data.model_dump(exclude_unset=True, exclude_none=True)
        raw_obj.update({"id": id})
        obj = await meta_data_tag_repo.update(MetaDataTag(**raw_obj))
        await meta_data_tag_repo.session.commit()
        return MetaDataTagUpdate.model_validate(obj)

    @delete(path="/{id:uuid}", tags=controller_tag)
    async def delete_item(
            self,
            meta_data_tag_repo: MetaDataTagRepository,
            id: UUID = Parameter(title="MetaData.py ID", description="The meta_data to delete.", ),
    ) -> None:
        """Delete a meta_data tag from the system."""
        _ = await meta_data_tag_repo.delete(id)
        await meta_data_tag_repo.session.commit()
