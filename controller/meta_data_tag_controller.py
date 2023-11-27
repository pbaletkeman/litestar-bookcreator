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

from model.meta_data_tag import MetaDataTag, MetaDataTagDTO, MetaDataTagCreate
from model.meta_data_tag_value import MetaDataTagValue

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


class MetaDataTagController(Controller):
    path = '/meta-data-tag'
    dependencies = {
        'meta_data_tag_repo': Provide(provide_meta_data_tag_repo),
    }
    meta_data_tag_controller_tag = ['Meta Data Tag - CRUD']

    @get(tags=meta_data_tag_controller_tag)
    async def list_meta_data_tags(
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

    @get('/details/{tag_id: int}', tags=meta_data_tag_controller_tag)
    async def get_meta_data_tag_details(self,
                                        meta_data_tag_repo: MetaDataTagRepository,
                                        tag_id: int = Parameter(title='Meta Data Tag ID',
                                                                description='The meta_data to update.', ),
                                        ) -> MetaDataTagDTO:
        """Interact with SQLAlchemy engine and session."""
        try:
            obj = await meta_data_tag_repo.get_one(id=tag_id)
            return MetaDataTagDTO.model_validate(obj)
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @post(tags=meta_data_tag_controller_tag)
    async def create_meta_data_tag(self, meta_data_tag_repo: MetaDataTagRepository,
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

    @route('/{tag_id:int}',
           http_method=[HttpMethod.PUT, HttpMethod.PATCH],
           tags=meta_data_tag_controller_tag)
    async def update_meta_data_tag(
            self,
            meta_data_tag_repo: MetaDataTagRepository,
            data: MetaDataTagCreate,
            tag_id: int = Parameter(title='Meta Data Tag ID', description='The meta_data to update.', ),
    ) -> MetaDataTagCreate:
        """Update an meta_data tag."""
        try:
            _data = data.model_dump(exclude_unset=True, exclude_none=True)
            _data.update({'id': tag_id})
            obj = await meta_data_tag_repo.update(MetaDataTag(**_data))
            await meta_data_tag_repo.session.commit()
            return MetaDataTagCreate.model_validate(obj)
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @delete('/{tag_id:int}', tags=meta_data_tag_controller_tag)
    async def delete_meta_data_tag(
            self,
            meta_data_tag_repo: MetaDataTagRepository,
            tag_id: int = Parameter(title='Meta Data Tag ID',
                                    description='The id meta data tag to delete.', ),
    ) -> None:
        """## Delete
         a meta_data tag from the system."""
        try:
            _ = await meta_data_tag_repo.delete(tag_id)
            await meta_data_tag_repo.session.commit()
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)


class MetaDataTagValueRepository(SQLAlchemyAsyncRepository[MetaDataTagValue]):
    """MetaData Tag repository."""

    model_type = MetaDataTagValue
