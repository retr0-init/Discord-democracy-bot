from __future__ import annotations
import asyncio
import datetime
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import selectinload

class Base(AsyncAttrs, DeclaritiveBase):
    pass

'''TODO
Add the table definition and check the database migration
'''
class User(Base):
    __table_name__ = "User"
    pass

class Vote(Base):
    __table_name__ = "Vote"
    pass

class Case(Base):
    __table_name__ = "Case"
    pass

class Punishment(Base):
    __table_name__ "Punishment"
    pass
