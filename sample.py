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
from pydantic import BaseModel as _BaseModel
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
from litestar.openapi import OpenAPIConfig
from litestar.params import Parameter
from litestar.repository.filters import LimitOffset

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from shared import BaseModel, SlugKey, SQLAlchemyAsyncSlugRepository, provide_limit_offset_pagination
from meta_data import MetaData, MetaDataRepository, MetaDataDTO, MetaDataCreate, MetaDataUpdate, provide_meta_data_repo, MetaDataController


session_config = AsyncSessionConfig(expire_on_commit=False)
sqlalchemy_config = SQLAlchemyAsyncConfig(
    connection_string="sqlite+aiosqlite:///test.sqlite", session_config=session_config
)  # Create 'async_session' dependency.
sqlalchemy_plugin = SQLAlchemyInitPlugin(config=sqlalchemy_config)


async def on_startup() -> None:
    """Initializes the database."""
    async with sqlalchemy_config.get_engine().begin() as conn:
        await conn.run_sync(UUIDAuditBase.metadata.create_all)


app = Litestar(
    route_handlers=[MetaDataController],
    openapi_config=OpenAPIConfig(
        title="My API", version="1.0.0",
        root_schema_site="elements",  # swagger, elements, redoc
        path="/docs",
        create_examples=False,
    ),
    exception_handlers={
        # exceptions.ApplicationError: exceptions.exception_to_http_response,
    },
    on_startup=[on_startup],
    plugins=[SQLAlchemyInitPlugin(config=sqlalchemy_config)],
    dependencies={"limit_offset": Provide(provide_limit_offset_pagination, sync_to_thread=False)},
)
