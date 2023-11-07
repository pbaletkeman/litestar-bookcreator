from __future__ import annotations

import random
import re
import string
import unicodedata
from typing import TYPE_CHECKING, Any
from uuid import UUID

from litestar import HttpMethod
from litestar import route
from litestar.pagination import OffsetPagination
# from pydantic import BaseModel as _BaseModel
from pydantic import TypeAdapter
from sqlalchemy.orm import Mapped, declarative_mixin, mapped_column
from sqlalchemy.types import String
from litestar import Controller
from litestar import Litestar, get, post, delete
from litestar.contrib.sqlalchemy.base import UUIDAuditBase
from litestar.contrib.sqlalchemy.plugins import AsyncSessionConfig, SQLAlchemyAsyncConfig, SQLAlchemyInitPlugin
from litestar.contrib.sqlalchemy.repository import (
    ModelT,
    SQLAlchemyAsyncRepository,
)
from litestar.di import Provide
from litestar.params import Parameter
from litestar.repository.filters import LimitOffset

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from shared import SlugKey, SQLAlchemyAsyncSlugRepository, BaseModel


# The `AuditBase` class includes the same UUID` based primary key (`id`) and 2
# additional columns: `created` and `updated`. `created` is a timestamp of when the
# record created, and `updated` is the last time the record was modified.
class MetaData(UUIDAuditBase, SlugKey):
    name: Mapped[str]
    description: Mapped[str]


class MetaDataRepository(SQLAlchemyAsyncSlugRepository[MetaData]):
    """Blog Post repository."""

    model_type = MetaData


class MetaDataDTO(BaseModel):
    id: UUID | None
    slug: str
    name: str
    description: str


class MetaDataCreate(BaseModel):
    name: str
    description: str


class MetaDataUpdate(BaseModel):
    name: str
    description: str


# async def get_available_slug(self, value_to_slugify: str, **kwargs: Any, ) -> str:
#     """Get a unique slug for the supplied value.
#
#     If the value is found to exist, a random 4 digit character is appended to the end.
#     There may be a better way to do this, but I wanted to limit the number of
#     additional database calls.
#
#     Args:
#         value_to_slugify (str): A string that should be converted to a unique slug.
#         **kwargs: stuff
#
#     Returns:
#         str: a unique slug for the supplied value. This is safe for URLs and other
#         unique identifiers.
#     """
#     slug = self._slugify(value_to_slugify)
#     if await self._is_slug_unique(slug):
#         return slug
#     # generate a random 4 digit alphanumeric string to make the slug unique and
#     # avoid another DB lookup.
#     random_string = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
#     return f"{slug}-{random_string}"


# @staticmethod
# def _slugify(value: str) -> str:
#     """slugify.
#
#     Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
#     dashes to single dashes. Remove characters that aren't alphanumerics,
#     underscores, or hyphens. Convert to lowercase. Also strip leading and
#     trailing whitespace, dashes, and underscores.
#
#     Args:
#         value (str): the string to slugify
#
#     Returns:
#         str: a slugified string of the value parameter
#     """
#     value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
#     value = re.sub(r"[^\w\s-]", "", value.lower())
#     return re.sub(r"[-\s]+", "-", value).strip("-_")


# async def _is_slug_unique(self, slug: str, **kwargs: Any, ) -> bool:
#     return await self.get_one_or_none(slug=slug) is None
#

# we can optionally override the default `select` used for the repository to pass in
# specific SQL options such as join details
async def provide_meta_data_repo(db_session: AsyncSession) -> MetaDataRepository:
    """This provides a simple example demonstrating how to override the join options
    for the repository."""
    return MetaDataRepository(session=db_session)


class MetaDataController(Controller):
    path = '/meta-data'
    controller_tag = ['Meta Data']

    dependencies = {"meta_data_repo": Provide(provide_meta_data_repo)}

    @get(path='/', tags=controller_tag)
    async def list_items(
        self,
        meta_data_repo: MetaDataRepository,
        limit_offset: LimitOffset,
    ) -> OffsetPagination[MetaDataDTO]:
        """List authors."""
        results, total = await meta_data_repo.list_and_count(limit_offset)
        type_adapter = TypeAdapter(list[MetaDataDTO])
        return OffsetPagination[MetaDataDTO](
            items=type_adapter.validate_python(results),
            total=total,
            limit=limit_offset.limit,
            offset=limit_offset.offset,
        )

    @get(path="/{item_slug:str}", tags=controller_tag)
    async def get_item_details(self, item_slug: str, meta_data_repo: MetaDataRepository, ) -> MetaDataDTO:
        """Interact with SQLAlchemy engine and session."""
        obj = await meta_data_repo.get_one(slug=item_slug)
        return MetaDataDTO.model_validate(obj)

    @post(path="/", tags=controller_tag)
    async def create_item(self, meta_data_repo: MetaDataRepository, data: MetaDataCreate, ) -> MetaDataDTO:
        """Create a new meta_data."""
        _data = data.model_dump(exclude_unset=True, by_alias=False, exclude_none=True)
        _data["slug"] = await meta_data_repo.get_available_slug(_data["name"])
        obj = await meta_data_repo.add(MetaData(**_data))
        await meta_data_repo.session.commit()
        return MetaDataDTO.model_validate(obj)

    @route(path="/{id:uuid}", http_method=[HttpMethod.PUT, HttpMethod.PATCH], tags=controller_tag)
    async def update_item(
        self,
        meta_data_repo: MetaDataRepository,
        data: MetaDataUpdate,
        id: UUID = Parameter(title="MetaData.py ID", description="The meta_data to update.", ),
    ) -> MetaDataUpdate:
        """Update an meta_data."""
        raw_obj = data.model_dump(exclude_unset=True, exclude_none=True)
        raw_obj.update({"id": id})
        obj = await meta_data_repo.update(MetaData(**raw_obj))
        await meta_data_repo.session.commit()
        return MetaDataUpdate.model_validate(obj)

    @delete(path="/{id:uuid}", tags=controller_tag)
    async def delete_item(
        self,
        meta_data_repo: MetaDataRepository,
        id: UUID = Parameter(title="MetaData.py ID", description="The meta_data to delete.", ),
    ) -> None:
        """Delete a meta_data from the system."""
        _ = await meta_data_repo.delete(id)
        await meta_data_repo.session.commit()
