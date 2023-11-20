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

from model.meta_data_attribute import MetaDataAttribute, MetaDataAttributeDTO, MetaDataAttributeCreate
from model.meta_data_tag import MetaDataTag, MetaDataTagDTO, MetaDataTagCreate
from model.meta_data_attribute_value import (MetaDataAttributeValue, MetaDataAttributeValueDTO,
                                             MetaDataAttributeValueCreate)
from model.meta_data_tag_value import MetaDataTagValue, MetaDataTagValueDTO

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from logger import logger


class MetaDataTagRepository(SQLAlchemyAsyncRepository[MetaDataTag]):
    """MetaData Tag repository."""

    model_type = MetaDataTag


# we can optionally override the default `select` used for the repository to pass in
# specific SQL options such as join details
async def provide_meta_data_tag_repo(db_session: AsyncSession) -> MetaDataTagRepository:
    """This provides a simple example demonstrating how to override the join options
    for the repository."""
    return MetaDataTagRepository(session=db_session)


class AttributeRepository(SQLAlchemyAsyncRepository[MetaDataAttribute]):
    """Attribute repository."""
    model_type = MetaDataAttribute


async def provide_attribute_repo(db_session: AsyncSession) -> AttributeRepository:
    """This provides a simple example demonstrating how to override the join options
    for the repository."""
    return AttributeRepository(
        session=db_session
    )


class MetaDataAttributeValueRepository(SQLAlchemyAsyncRepository[MetaDataAttributeValue]):
    """MetaData Tag repository."""

    model_type = MetaDataAttributeValue


class AttributeController(Controller):
    attribute_controller_tag = ['Attribute - CRUD']
    attribute_path = '/attribute'

    dependencies = {"attribute_repo": Provide(provide_attribute_repo),
                    }

    @get(path=attribute_path, tags=attribute_controller_tag)
    async def list_attribute_items(
            self,
            attribute_repo: AttributeRepository,
            limit_offset: LimitOffset,
    ) -> OffsetPagination[MetaDataAttributeDTO]:
        """List items."""
        # alternative way to query tables
        # stmt = lambda_stmt(lambda: select(Attribute))
        # stmt += lambda s: s.where(Attribute.meta_data_tag_id == meta_data_tag_id)
        # results, total = await attribute_repo.list_and_count(limit_offset, statement=stmt)

        try:
            order_by1 = OrderBy(field_name=MetaDataAttribute.sort_order)
            order_by2 = OrderBy(field_name=MetaDataAttribute.name)
            results, total = await attribute_repo.list_and_count(limit_offset,
                                                                 order_by1,
                                                                 order_by2)
            type_adapter = TypeAdapter(list[MetaDataAttributeDTO])
            return OffsetPagination[MetaDataAttributeDTO](
                items=type_adapter.validate_python(results),
                total=total,
                limit=limit_offset.limit,
                offset=limit_offset.offset,
            )
        except advanced_alchemy.exceptions.RepositoryError as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @get(path='/details/' + attribute_path + '/{attribute_id: int}',
         tags=attribute_controller_tag)
    async def get_attribute_item_details(self,
                                         attribute_repo: AttributeRepository,
                                         attribute_id: int = Parameter(title="Meta Data Tag ID",
                                                                       description="The meta_data to update.", ),
                                         ) -> MetaDataAttributeDTO:
        try:
            obj = await attribute_repo.get_one(id=attribute_id)
            return MetaDataAttributeDTO.model_validate(obj)
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @post(path=attribute_path, tags=attribute_controller_tag)
    async def create_attribute_item(self,
                                    attribute_repo: AttributeRepository,
                                    data: MetaDataAttributeCreate,
                                    ) -> MetaDataAttributeDTO:
        try:
            _data = data.model_dump(exclude_unset=True, by_alias=False, exclude_defaults=True)
            obj = await attribute_repo.add(MetaDataAttribute(**_data))
            await attribute_repo.session.commit()
            return MetaDataAttributeDTO.model_validate(obj)
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @route(path=attribute_path + '/{attribute_id: int}',
           http_method=[HttpMethod.PUT, HttpMethod.PATCH],
           tags=attribute_controller_tag)
    async def update_attribute_item(self,
                                    attribute_repo: AttributeRepository,
                                    data: MetaDataAttributeCreate,
                                    attribute_id: int = Parameter(title="Meta Data Tag ID",
                                                                  description="The meta_data to update.", ),
                                    ) -> MetaDataAttributeCreate:
        try:
            _data = data.model_dump(exclude_unset=True, exclude_defaults=True)
            _data["id"] = attribute_id
            # verify that the record is there before trying operation
            obj = await attribute_repo.update(MetaDataAttribute(**_data), with_for_update=True)
            await attribute_repo.session.commit()
            return MetaDataAttributeCreate.model_validate(obj)
        except Exception as ex:
            logger.error(ex)
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @delete(path=attribute_path + '/{attribute_id: int}', tags=attribute_controller_tag)
    async def delete_attribute_item(self,
                                    attribute_repo: AttributeRepository,
                                    attribute_id: int = Parameter(title="Meta Data Tag ID",
                                                                  description="The meta_data to update.", ),
                                    ) -> None:
        try:
            # verify that the record is there before trying operation
            _ = await attribute_repo.delete(attribute_id)
            await attribute_repo.session.commit()
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)


class MetaDataTagController(Controller):
    # path = '/meta-data-tag'
    dependencies = {
        "meta_data_tag_repo": Provide(provide_meta_data_tag_repo),
    }
    meta_data_tag_controller_tag = ['Meta Data Tag - CRUD']
    meta_data_tag_path = '/meta-data-tag'

    @get(path=meta_data_tag_path, tags=meta_data_tag_controller_tag)
    async def list_meta_data_tag_items(
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

    @get(path='/details/' + meta_data_tag_path + "/{meta_data_tag_id: int}", tags=meta_data_tag_controller_tag)
    async def get_meta_data_tag_details(self,
                                        meta_data_tag_repo: MetaDataTagRepository,
                                        meta_data_tag_id: int = Parameter(title="Meta Data Tag ID",
                                                                          description="The meta_data to update.", ),
                                        ) -> MetaDataTagDTO:
        """Interact with SQLAlchemy engine and session."""
        try:
            obj = await meta_data_tag_repo.get_one(id=meta_data_tag_id)
            return MetaDataTagDTO.model_validate(obj)
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @post(path=meta_data_tag_path, tags=meta_data_tag_controller_tag)
    async def create_meta_data_tag_item(self, meta_data_tag_repo: MetaDataTagRepository,
                                        data: MetaDataTagCreate, ) -> MetaDataTagDTO:
        """Create a new meta_data tag."""
        try:
            _data = data.model_dump(exclude_unset=True, by_alias=False, exclude_none=True)
            # _data["slug"] = await meta_data_tag_repo.get_available_slug(_data["name"])
            obj = await meta_data_tag_repo.add(MetaDataTag(**_data))
            await meta_data_tag_repo.session.commit()
            return MetaDataTagDTO.model_validate(obj)
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @route(path=meta_data_tag_path + "/{meta_data_tag_id:int}",
           http_method=[HttpMethod.PUT, HttpMethod.PATCH],
           tags=meta_data_tag_controller_tag)
    async def update_meta_data_tag_item(
            self,
            meta_data_tag_repo: MetaDataTagRepository,
            data: MetaDataTagCreate,
            meta_data_tag_id: int = Parameter(title="Meta Data Tag ID", description="The meta_data to update.", ),
    ) -> MetaDataTagCreate:
        """Update an meta_data tag."""
        try:
            _data = data.model_dump(exclude_unset=True, exclude_none=True)
            _data.update({"id": meta_data_tag_id})
            obj = await meta_data_tag_repo.update(MetaDataTag(**_data))
            await meta_data_tag_repo.session.commit()
            return MetaDataTagCreate.model_validate(obj)
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @delete(path=meta_data_tag_path + "/{meta_data_tag_id:int}", tags=meta_data_tag_controller_tag)
    async def delete_meta_data_tag_item(
            self,
            meta_data_tag_repo: MetaDataTagRepository,
            meta_data_tag_id: int = Parameter(title="Meta Data Tag ID",
                                              description="The id meta data tag to delete.", ),
    ) -> None:
        """## Delete
         a meta_data tag from the system."""
        try:
            _ = await meta_data_tag_repo.delete(meta_data_tag_id)
            await meta_data_tag_repo.session.commit()
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)
