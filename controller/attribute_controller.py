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

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from logger import logger


class AttributeRepository(SQLAlchemyAsyncRepository[MetaDataAttribute]):
    """Attribute repository."""
    model_type = MetaDataAttribute


async def provide_attribute_repo(db_session: AsyncSession) -> AttributeRepository:
    """This provides a simple example demonstrating how to override the join options
    for the repository."""
    return AttributeRepository(
        session=db_session
    )


class AttributeController(Controller):
    attribute_controller_tag = ['Attribute - CRUD']
    path = '/attribute'

    dependencies = {"attribute_repo": Provide(provide_attribute_repo),
                    }

    @get(tags=attribute_controller_tag)
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

    @get('/details/{attribute_id: int}',
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

    @post(tags=attribute_controller_tag)
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

    @route('/{attribute_id: int}',
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

    @delete('/{attribute_id: int}', tags=attribute_controller_tag)
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


