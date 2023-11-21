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

from model.meta_data import MetaData, MetaDataDTO, MetaDataCreate
from model.meta_data_tag_value import MetaDataTagValue
from model.meta_data_attribute_value import MetaDataAttributeValue

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from logger import logger


class MetaDataRepository(SQLAlchemyAsyncRepository[MetaData]):
    """MetaData Tag repository."""

    model_type = MetaData


class MetaDataTagValueRepository(SQLAlchemyAsyncRepository[MetaDataTagValue]):
    """MetaData Tag repository."""

    model_type = MetaDataTagValue


class MetaDataAttributeValueRepository(SQLAlchemyAsyncRepository[MetaDataAttributeValue]):
    """MetaData Tag repository."""

    model_type = MetaDataAttributeValue


# we can optionally override the default `select` used for the repository to pass in
# specific SQL options such as join details
async def provide_meta_data_repo(db_session: AsyncSession) -> MetaDataRepository:
    """This provides a simple example demonstrating how to override the join options
    for the repository."""
    return MetaDataRepository(session=db_session)


class MetaDataController(Controller):
    path = '/meta-data'
    dependencies = {
        "meta_data_repo": Provide(provide_meta_data_repo),
    }
    meta_data_controller_tag = ['Meta Data - CRUD']

    @get(tags=meta_data_controller_tag)
    async def list_meta_data_items(
            self,
            meta_data_repo: MetaDataRepository,
            limit_offset: LimitOffset,
    ) -> OffsetPagination[MetaDataDTO]:
        """List items."""
        try:
            order_by2 = OrderBy(field_name=MetaData.name)
            results, total = await meta_data_repo.list_and_count(limit_offset, order_by2)
            type_adapter = TypeAdapter(list[MetaDataDTO])
            return OffsetPagination[MetaDataDTO](
                items=type_adapter.validate_python(results),
                total=total,
                limit=limit_offset.limit,
                offset=limit_offset.offset,
            )
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @get("/details/{meta_data_id: int}", tags=meta_data_controller_tag)
    async def get_meta_data_details(self,
                                    meta_data_repo: MetaDataRepository,
                                    meta_data_id: int = Parameter(title="Meta Data Tag ID",
                                                                  description="The meta_data to update.", ),
                                    ) -> MetaDataDTO:
        """Interact with SQLAlchemy engine and session."""
        try:
            obj = await meta_data_repo.get_one(id=meta_data_id)
            return MetaDataDTO.model_validate(obj)
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @post(tags=meta_data_controller_tag)
    async def create_meta_data_tag_item(self, meta_data_repo: MetaDataRepository,
                                        data: MetaDataCreate, ) -> MetaDataDTO:
        """Create a new meta_data tag."""
        try:
            _data = data.model_dump(exclude_unset=True, by_alias=False, exclude_none=True)
            # _data["slug"] = await meta_data_tag_repo.get_available_slug(_data["name"])
            obj = await meta_data_repo.add(MetaData(**_data))
            await meta_data_repo.session.commit()
            return MetaDataDTO.model_validate(obj)
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @route("/{meta_data_id:int}",
           http_method=[HttpMethod.PUT, HttpMethod.PATCH],
           tags=meta_data_controller_tag)
    async def update_meta_data_item(
            self,
            meta_data_repo: MetaDataRepository,
            data: MetaDataCreate,
            meta_data_id: int = Parameter(title="Meta Data Tag ID", description="The meta_data to update.", ),
    ) -> MetaDataCreate:
        """Update an meta_data tag."""
        try:
            _data = data.model_dump(exclude_unset=True, exclude_none=True)
            _data.update({"id": meta_data_id})
            obj = await meta_data_repo.update(MetaData(**_data))
            await meta_data_repo.session.commit()
            return MetaDataCreate.model_validate(obj)
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @delete("/{meta_data_id:int}", tags=meta_data_controller_tag)
    async def delete_meta_data_tag_item(
            self,
            meta_data_repo: MetaDataRepository,
            meta_data_id: int = Parameter(title="Meta Data Tag ID",
                                          description="The id meta data tag to delete.", ),
    ) -> None:
        """## Delete
         a meta_data tag from the system."""
        try:
            _ = await meta_data_repo.delete(meta_data_id)
            await meta_data_repo.session.commit()
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)
