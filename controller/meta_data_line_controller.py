from __future__ import annotations

from typing import TYPE_CHECKING, List

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

from model.meta_data_attribute_value import MetaDataAttributeValue
from model.meta_data_line import MetaDataLine, MetaDataLineDTO, MetaDataLineCreate, MetaDataValueCreate
from model.meta_data_tag_value import MetaDataTagValue

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class MetaDataAttributeValueRepository(SQLAlchemyAsyncRepository[MetaDataAttributeValue]):
    """MetaData Line repository."""
    model_type = MetaDataAttributeValue


class MetaDataTagValueRepository(SQLAlchemyAsyncRepository[MetaDataTagValue]):
    model_type = MetaDataTagValue


class MetaDataLineRepository(SQLAlchemyAsyncRepository[MetaDataLine]):
    """MetaData Line repository."""
    model_type = MetaDataLine


# we can optionally override the default `select` used for the repository to pass in
# specific SQL options such as join details
async def provide_meta_data_line_repo(db_session: AsyncSession) -> MetaDataLineRepository:
    """This provides a simple example demonstrating how to override the join options
    for the repository."""
    return MetaDataLineRepository(session=db_session)


async def provide_meta_data_tag_value_repo(db_session: AsyncSession) -> MetaDataTagValueRepository:
    return MetaDataTagValueRepository(session=db_session)


async def provide_meta_data_attribute_value_repo(db_session: AsyncSession) -> MetaDataAttributeValueRepository:
    return MetaDataAttributeValueRepository(session=db_session)


class MetaDataController(Controller):
    path = '/meta-data-line'
    dependencies = {
        'meta_data_line_repo': Provide(provide_meta_data_line_repo),
        'meta_data_tag_value_repo': Provide(provide_meta_data_tag_value_repo),
        'meta_data_attribute_value_repo': Provide(provide_meta_data_attribute_value_repo)
    }
    meta_data_line_controller_tag = ['Meta Data Line - CRUD']

    @get(tags=meta_data_line_controller_tag)
    async def list_meta_data_lines(
            self,
            meta_data_line_repo: MetaDataLineRepository,
            limit_offset: LimitOffset,
    ) -> OffsetPagination[MetaDataLineDTO]:
        """List items."""
        try:
            order_by2 = OrderBy(field_name=MetaDataLine.name)
            results, total = await meta_data_line_repo.list_and_count(limit_offset, order_by2)
            type_adapter = TypeAdapter(list[MetaDataLineDTO])
            return OffsetPagination[MetaDataLineDTO](
                items=type_adapter.validate_python(results),
                total=total,
                limit=limit_offset.limit,
                offset=limit_offset.offset,
            )
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @get('/details/{line_id: int}', tags=meta_data_line_controller_tag)
    async def get_meta_data_line_details(self,
                                         meta_data_line_repo: MetaDataLineRepository,
                                         line_id: int = Parameter(title='Meta Data Tag ID',
                                                                  description='The meta_data to update.', ),
                                         ) -> MetaDataLineDTO:
        """Interact with SQLAlchemy engine and session."""
        try:
            obj = await meta_data_line_repo.get_one(id=line_id)
            return MetaDataLineDTO.model_validate(obj)
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @post(tags=meta_data_line_controller_tag)
    async def create_meta_data_line(self,
                                    meta_data_line_repo: MetaDataLineRepository,
                                    meta_data_tag_value_repo: MetaDataTagValueRepository,
                                    data: MetaDataLineCreate, ) -> MetaDataLineDTO:
        """Create a new meta_data tag."""
        try:
            _data = data.model_dump(exclude_unset=True, by_alias=False, exclude_none=True)
            # get json element as a class
            tag: MetaDataTagValue = _data.pop('tag')
            saved_line: MetaDataLine = await meta_data_line_repo.add(MetaDataLine(**_data))
            await meta_data_line_repo.session.commit()
            # add foreign key of the record that was just saved
            tag.update({'line_id': saved_line.id})
            saved_tag: MetaDataTagValue = await meta_data_tag_value_repo.add(**tag)
            await meta_data_tag_value_repo.session.commit()
            return tag
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @route('/{line_id:int}',
           http_method=[HttpMethod.PUT, HttpMethod.PATCH],
           tags=meta_data_line_controller_tag)
    async def update_meta_data_line(
            self,
            meta_data_line_repo: MetaDataLineRepository,
            data: MetaDataLineCreate,
            line_id: int = Parameter(title='Meta Data Tag ID', description='The meta_data to update.', ),
    ) -> MetaDataLineCreate:
        """Update an meta_data tag."""
        try:
            _data = data.model_dump(exclude_unset=True, exclude_none=True)
            _data.update({"id": line_id})
            obj = await meta_data_line_repo.update(MetaDataLine(**_data))
            await meta_data_line_repo.session.commit()
            return MetaDataLineCreate.model_validate(obj)
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)

    @delete('/{line_id:int}', tags=meta_data_line_controller_tag)
    async def delete_meta_data_lines(
            self,
            meta_data_line_repo: MetaDataLineRepository,
            line_id: int = Parameter(title='Meta Data Tag ID',
                                     description='The id meta data tag to delete.', ),
    ) -> None:
        """## Delete
         a meta_data tag from the system."""
        try:
            _ = await meta_data_line_repo.delete(line_id)
            await meta_data_line_repo.session.commit()
        except Exception as ex:
            raise HTTPException(detail=str(ex), status_code=status_codes.HTTP_404_NOT_FOUND)


"""
{
  "name":"string",
  "tag":{
     "tag_id":1,
     "value":"nul"
  },
  "attributes":[
    {
        "id":1,
        "value":"a"
    }
  ]
}
"""
