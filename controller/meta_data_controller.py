from __future__ import annotations

from typing import TYPE_CHECKING

import advanced_alchemy
from litestar.exceptions import HTTPException
from litestar import status_codes
from advanced_alchemy import SQLAlchemyAsyncRepository
from litestar import Controller
from litestar import HttpMethod
from litestar import get, post, delete
from litestar import route
from litestar.di import Provide
from litestar.pagination import OffsetPagination
from litestar.params import Parameter
from litestar.repository.filters import LimitOffset, OrderBy
from pydantic import TypeAdapter

from model.meta_data import Attribute, MetaDataTag, AttributeDTO, AttributeCreate, AttributeUpdate, MetaDataTagDTO, \
    MetaDataTagCreate, MetaDataTagUpdate

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from shared import SQLAlchemyAsyncSlugRepository
from logger import logger


class AttributeRepository(SQLAlchemyAsyncRepository[Attribute]):
    """Blog Post repository."""
    model_type = Attribute


class MetaDataTagRepository(SQLAlchemyAsyncSlugRepository[MetaDataTag]):
    """Blog Post repository."""

    model_type = MetaDataTag


# we can optionally override the default `select` used for the repository to pass in
# specific SQL options such as join details
async def provide_attribute_repo(db_session: AsyncSession) -> AttributeRepository:
    """This provides a simple example demonstrating how to override the join options
    for the repository."""
    return AttributeRepository(session=db_session)


# we can optionally override the default `select` used for the repository to pass in
# specific SQL options such as join details
async def provide_meta_data_tag_repo(db_session: AsyncSession) -> MetaDataTagRepository:
    """This provides a simple example demonstrating how to override the join options
    for the repository."""
    return MetaDataTagRepository(session=db_session)


class MetaDataTagController(Controller):
    path = '/meta-data-tag'
    meta_data_controller_tag = ['Meta Data - CRUD']
    attribute_controller_tag = ['Attribute - CRUD']
    attribute_path = '/attribute'

    dependencies = {"meta_data_tag_repo": Provide(provide_meta_data_tag_repo),
                    "attribute_repo": Provide(provide_attribute_repo)}

    @get(path='/{meta_data_tag_id:int}' + attribute_path, tags=attribute_controller_tag)
    async def list_attribute_items(
            self,
            meta_data_tag_id: int,
            attribute_repo: AttributeRepository,
            limit_offset: LimitOffset,
    ) -> OffsetPagination[AttributeDTO]:
        """List items."""
        # alternative way to query tables
        # stmt = lambda_stmt(lambda: select(Attribute))
        # stmt += lambda s: s.where(Attribute.meta_data_tag_id == meta_data_tag_id)
        # results, total = await attribute_repo.list_and_count(limit_offset, statement=stmt)

        try:
            order_by1 = OrderBy(field_name=Attribute.sort_order)
            order_by2 = OrderBy(field_name=Attribute.name)
            results, total = await attribute_repo.list_and_count(limit_offset,
                                                                 order_by1,
                                                                 order_by2,
                                                                 id=meta_data_tag_id)
            type_adapter = TypeAdapter(list[AttributeDTO])
            return OffsetPagination[AttributeDTO](
                items=type_adapter.validate_python(results),
                total=total,
                limit=limit_offset.limit,
                offset=limit_offset.offset,
            )
        except advanced_alchemy.exceptions.RepositoryError as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @get(path='/{meta_data_tag_id: int}' + attribute_path + '/{attribute_id: int}', tags=attribute_controller_tag)
    async def get_attribute_item_details(self,
                                         meta_data_tag_id: int,
                                         attribute_id: int,
                                         attribute_repo: AttributeRepository, ) -> AttributeDTO:
        try:
            obj = await attribute_repo.get_one(id=attribute_id, meta_data_tag_id=meta_data_tag_id)
            return AttributeDTO.model_validate(obj)
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @post(path='/{meta_data_tag_id: int}' + attribute_path, tags=attribute_controller_tag)
    async def create_attribute_item(self,
                                    meta_data_tag_id: int,
                                    attribute_repo: AttributeRepository,
                                    data: AttributeCreate, ) -> AttributeDTO:
        try:
            _data = data.model_dump(exclude_unset=True, by_alias=False, exclude_defaults=True)
            _data["meta_data_tag_id"] = meta_data_tag_id
            obj = await attribute_repo.add(Attribute(**_data))
            await attribute_repo.session.commit()
            return AttributeDTO.model_validate(obj)
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @route(path='/{meta_data_tag_id: int}' + attribute_path + '/{attribute_id: int}',
           http_method=[HttpMethod.PUT, HttpMethod.PATCH],
           tags=attribute_controller_tag)
    async def update_attribute_item(self,
                                    attribute_repo: AttributeRepository,
                                    data: AttributeUpdate,
                                    _: int,
                                    attribute_id: int) -> AttributeUpdate:
        try:
            _data = data.model_dump(exclude_unset=True, exclude_defaults=True)
            _data["id"] = attribute_id
            obj = await attribute_repo.update(Attribute(**_data), with_for_update=True)
            await attribute_repo.session.commit()
            return AttributeUpdate.model_validate(obj)
        except Exception as ex:
            logger.error(ex)
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @delete(path='/{meta_data_tag_id: int}' + attribute_path + '/{attribute_id: int}', tags=attribute_controller_tag)
    async def delete_attribute_item(self,
                                    attribute_repo: AttributeRepository,
                                    _: int,
                                    attribute_id: int) -> None:
        try:
            _ = await attribute_repo.delete(attribute_id)
            await attribute_repo.session.commit()
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @get(path='/', tags=meta_data_controller_tag)
    async def list_meta_data_items(
            self,
            meta_data_tag_repo: MetaDataTagRepository,
            limit_offset: LimitOffset,
    ) -> OffsetPagination[MetaDataTagDTO]:
        """List items."""
        try:
            order_by1 = OrderBy(field_name=MetaDataTag.sort_order)
            order_by2 = OrderBy(field_name=MetaDataTag.name)
            results, total = await meta_data_tag_repo.list_and_count(limit_offset, order_by1, order_by2)
            type_adapter = TypeAdapter(list[MetaDataTagDTO])
            return OffsetPagination[MetaDataTagDTO](
                items=type_adapter.validate_python(results),
                total=total,
                limit=limit_offset.limit,
                offset=limit_offset.offset,
            )
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @get(path="/{item_slug:str}", tags=meta_data_controller_tag)
    async def get_meta_data_details(self, item_slug: str,
                                    meta_data_tag_repo: MetaDataTagRepository, ) -> MetaDataTagDTO:
        """Interact with SQLAlchemy engine and session."""
        try:
            obj = await meta_data_tag_repo.get_one(slug=item_slug)
            return MetaDataTagDTO.model_validate(obj)
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

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
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @route(path="/{meta_data_tag_id:int}",
           http_method=[HttpMethod.PUT, HttpMethod.PATCH],
           tags=meta_data_controller_tag)
    async def update_meta_data_item(
            self,
            meta_data_tag_repo: MetaDataTagRepository,
            data: MetaDataTagUpdate,
            meta_data_tag_id: int = Parameter(title="MetaData.py ID", description="The meta_data to update.", ),
    ) -> MetaDataTagUpdate:
        """Update an meta_data tag."""
        try:
            _data = data.model_dump(exclude_unset=True, exclude_none=True)
            _data.update({"id": meta_data_tag_id})
            obj = await meta_data_tag_repo.update(MetaDataTag(**_data))
            await meta_data_tag_repo.session.commit()
            return MetaDataTagUpdate.model_validate(obj)
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @delete(path="/{meta_data_tag_id:int}", tags=meta_data_controller_tag)
    async def delete_meta_data_item(
            self,
            meta_data_tag_repo: MetaDataTagRepository,
            meta_data_tag_id: int = Parameter(title="MetaData.py ID", description="The meta_data to delete.", ),
    ) -> None:
        """Delete a meta_data tag from the system."""
        try:
            _ = await meta_data_tag_repo.delete(meta_data_tag_id)
            await meta_data_tag_repo.session.commit()
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)
