from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from litestar import Litestar
from litestar.config.compression import CompressionConfig
from litestar.contrib.sqlalchemy.base import UUIDAuditBase
from litestar.contrib.sqlalchemy.plugins import AsyncSessionConfig, SQLAlchemyAsyncConfig, SQLAlchemyInitPlugin
from litestar.di import Provide
from litestar.openapi import OpenAPIConfig

from controller.meta_data_controller import MetaDataTagController

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from shared import provide_limit_offset_pagination
# from meta_data import MetaDataTagController

session_config = AsyncSessionConfig(expire_on_commit=False)
sqlalchemy_config = SQLAlchemyAsyncConfig(
    # connection_string="sqlite+aiosqlite:///test.sqlite", session_config=session_config
    connection_string="postgresql+asyncpg://pete:pete@host.docker.internal:5432/sample_project",
    session_config=session_config

)  # Create 'async_session' dependency.
sqlalchemy_plugin = SQLAlchemyInitPlugin(config=sqlalchemy_config)

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


async def on_startup() -> None:
    """Initializes the database."""
    async with sqlalchemy_config.get_engine().begin() as conn:
        await conn.run_sync(UUIDAuditBase.metadata.create_all)


app = Litestar(
    route_handlers=[MetaDataTagController],
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
    compression_config=CompressionConfig(backend="gzip", gzip_compress_level=9),
)
