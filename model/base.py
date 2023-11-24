from __future__ import annotations

from advanced_alchemy.base import AuditColumns
from pydantic import BaseModel as _BaseModel
from sqlalchemy import String
from sqlalchemy.orm import declarative_mixin, Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase, AuditColumns):
    """Base for SQLAlchemy declarative models in this project with int primary keys."""

    pass


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {'from_attributes': True}


# we are going to add a simple "slug" to our model that is a URL safe surrogate key to
# our database record.
@declarative_mixin
class SlugKey:
    """Slug unique Field Model Mixin."""

    __abstract__ = True
    slug: Mapped[str] = mapped_column(String(length=100), nullable=False, unique=True, sort_order=99)
