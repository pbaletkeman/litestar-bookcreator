from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, Optional, List
from uuid import UUID

import advanced_alchemy
import sqlalchemy.exc
from advanced_alchemy import SQLAlchemyAsyncRepository
from litestar import HttpMethod
from litestar import route
from litestar.pagination import OffsetPagination
from pydantic import TypeAdapter
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import asyncpg
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
from logger import logger


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


class AttributeRepository(SQLAlchemyAsyncRepository[Attribute]):
    """Blog Post repository."""
    model_type = Attribute


class AttributeDTO(BaseModel):
    id: int | None
    sort_order: Optional[int] = 0
    name: str
    description: Optional[str] = None
    meta_data_tag_id: UUID


class AttributeCreate(BaseModel):
    name: str
    sort_order: Optional[int] = 0
    description: Optional[str] = None
    # meta_data_tag_id: UUID


class AttributeUpdate(BaseModel):
    name: str
    sort_order: Optional[int] = 0
    description: Optional[str] = None
    # meta_data_tag_id: UUID


# we can optionally override the default `select` used for the repository to pass in
# specific SQL options such as join details
async def provide_attribute_repo(db_session: AsyncSession) -> AttributeRepository:
    """This provides a simple example demonstrating how to override the join options
    for the repository."""
    return AttributeRepository(session=db_session)


class MetaDataTagController(Controller):
    path = '/meta-data-tag'
    meta_data_controller_tag = ['Meta Data']
    attribute_controller_tag = ['Attribute']
    attribute_path = '/attribute'

    dependencies = {"meta_data_tag_repo": Provide(provide_meta_data_tag_repo),
                    "attribute_repo": Provide(provide_attribute_repo)}

    @get(path='/{meta_data_tag_id:str}' + attribute_path, tags=attribute_controller_tag)
    async def list_attribute_items(
            self,
            meta_data_tag_id: str,
            attribute_repo: AttributeRepository,
            limit_offset: LimitOffset,
    ) -> OffsetPagination[AttributeDTO]:
        """List items."""
        # alternative way to query tables
        # stmt = lambda_stmt(lambda: select(Attribute))
        # stmt += lambda s: s.where(Attribute.meta_data_tag_id == meta_data_tag_id)
        # results, total = await attribute_repo.list_and_count(limit_offset, statement=stmt)

        try:
            results, total = await attribute_repo.list_and_count(limit_offset, meta_data_tag_id=meta_data_tag_id)
            type_adapter = TypeAdapter(list[AttributeDTO])
            return OffsetPagination[AttributeDTO](
                items=type_adapter.validate_python(results),
                total=total,
                limit=limit_offset.limit,
                offset=limit_offset.offset,
            )
        except advanced_alchemy.exceptions.RepositoryError as ex:
            logger.error(ex)

    @get(path='/{meta_data_tag_id:str}' + attribute_path + '/{id: int}', tags=attribute_controller_tag)
    async def get_attribute_item_details(self,
                                         meta_data_tag_id: str,
                                         id: int,
                                         attribute_repo: AttributeRepository, ) -> AttributeDTO:
        try:
            obj = await attribute_repo.get_one(id=id, meta_data_tag_id=meta_data_tag_id)
            return AttributeDTO.model_validate(obj)
        except Exception as ex:
            logger.error(ex)

    @post(path='/{meta_data_tag_id:str}' + attribute_path, tags=attribute_controller_tag)
    async def create_attribute_item(self,
                                    meta_data_tag_id: str,
                                    attribute_repo: AttributeRepository,
                                    data: AttributeCreate, ) -> AttributeDTO:
        try:
            _data = data.model_dump(exclude_unset=True, by_alias=False, exclude_defaults=True)
            _data["meta_data_tag_id"] = meta_data_tag_id
            obj = await attribute_repo.add(Attribute(**_data))
            await attribute_repo.session.commit()
            return AttributeDTO.model_validate(obj)
        except Exception as ex:
            logger.error(ex)

    @route(path='/{meta_data_tag_id:str}' + attribute_path + '/{id: int}',
           http_method=[HttpMethod.PUT, HttpMethod.PATCH],
           tags=attribute_controller_tag)
    async def update_attribute_item(self,
                                    attribute_repo: AttributeRepository,
                                    data: AttributeUpdate,
                                    meta_data_tag_id: str,
                                    id: int) -> AttributeUpdate:
        try:
            _data = data.model_dump(exclude_unset=True, exclude_defaults=True)
            _data["id"] = id
            obj = await attribute_repo.update(Attribute(**_data), with_for_update=True)
            await attribute_repo.session.commit()
            return AttributeUpdate.model_validate(obj)
        except Exception as ex:
            logger.error(ex)

    @delete(path='/{meta_data_tag_id:str}' + attribute_path + '/{id: int}', tags=attribute_controller_tag)
    async def delete_attribute_item(self, attribute_repo: AttributeRepository, id: int) -> None:
        try:
            _ = await attribute_repo.delete(id)
            await attribute_repo.session.commit()
        except Exception as ex:
            logger.error(ex)

    @get(path='/', tags=meta_data_controller_tag)
    async def list_meta_data_items(
            self,
            meta_data_tag_repo: MetaDataTagRepository,
            limit_offset: LimitOffset,
    ) -> OffsetPagination[MetaDataTagDTO]:
        """List items."""
        try:
            results, total = await meta_data_tag_repo.list_and_count(limit_offset)
            type_adapter = TypeAdapter(list[MetaDataTagDTO])
            return OffsetPagination[MetaDataTagDTO](
                items=type_adapter.validate_python(results),
                total=total,
                limit=limit_offset.limit,
                offset=limit_offset.offset,
            )
        except Exception as ex:
            logger.error(ex)

    @get(path="/{item_slug:str}", tags=meta_data_controller_tag)
    async def get_meta_data_details(self, item_slug: str,
                                    meta_data_tag_repo: MetaDataTagRepository, ) -> MetaDataTagDTO:
        """Interact with SQLAlchemy engine and session."""
        try:
            obj = await meta_data_tag_repo.get_one(slug=item_slug)
            return MetaDataTagDTO.model_validate(obj)
        except Exception as ex:
            logger.error(ex)

    @post(path="/", tags=meta_data_controller_tag)
    async def create_meta_data_item(self, meta_data_tag_repo: MetaDataTagRepository,
                                    data: MetaDataTagCreate, ) -> MetaDataTagDTO:
        """Create a new meta_data tag."""
        try:
            _data = data.model_dump(exclude_unset=True, by_alias=False, exclude_none=True)
            _data["slug"] = await meta_data_tag_repo.get_available_slug(_data["name"])
            obj = await meta_data_tag_repo.add(MetaDataTag(**_data))
            await meta_data_tag_repo.session.commit()
            return MetaDataTagDTO.model_validate(obj)
        except Exception as ex:
            logger.error(ex)

    @route(path="/{id:uuid}", http_method=[HttpMethod.PUT, HttpMethod.PATCH], tags=meta_data_controller_tag)
    async def update_meta_data_item(
            self,
            meta_data_tag_repo: MetaDataTagRepository,
            data: MetaDataTagUpdate,
            id: UUID = Parameter(title="MetaData.py ID", description="The meta_data to update.", ),
    ) -> MetaDataTagUpdate:
        """Update an meta_data tag."""
        try:
            _data = data.model_dump(exclude_unset=True, exclude_none=True)
            _data.update({"id": id})
            obj = await meta_data_tag_repo.update(MetaDataTag(**_data))
            await meta_data_tag_repo.session.commit()
            return MetaDataTagUpdate.model_validate(obj)
        except Exception as ex:
            logger.error(ex)

    @delete(path="/{id:uuid}", tags=meta_data_controller_tag)
    async def delete_meta_data_item(
            self,
            meta_data_tag_repo: MetaDataTagRepository,
            id: UUID = Parameter(title="MetaData.py ID", description="The meta_data to delete.", ),
    ) -> None:
        """Delete a meta_data tag from the system."""
        try:
            _ = await meta_data_tag_repo.delete(id)
            await meta_data_tag_repo.session.commit()
        except Exception as ex:
            logger.error(ex)
