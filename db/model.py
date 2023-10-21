from __future__ import annotations
import asyncio
import datetime
from typing import List
from typing import Optional
import enum
import uuid

from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ARRAY
from sqlalchemy import Uuid
from sqlalchemy import Enum
from sqlalchemy import UnicodeText
from sqlalchemy import Boolean

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

'''TODO
- Check the project folder structure when doing the import
'''
from bot_types_enum import VoteTypeEnum, PunishmentTypeEnum
from bot_types_enum import CaseStepEnum, CaseWinnerEnum, PunishmentAuthorityEnum

class Base(AsyncAttrs, DeclaritiveBase):
    pass

'''TODO
- Check the database migration
- Check the optional and nullable fields
- Improve the definition for better database integrity
- Check against the async IO capabilities of this database
    - Queue push?
    - Or just await async functions provided?
- Check how to store original Python object list as a table column
    - Type[Any] from typing?
- Improvements optional: add 
'''
class User(Base):
    __table_name__ = "User"

    id:             Mapped[int]                 = mapped_column(primary_key=True)
    join_date:      Mapped[datetime.datetime)   = mapped_column(DateTime)
    # Get the discord role object with discord.utils.get() and these role id's
    roles                                       = mapped_column(ARRAY(Integer))
    punishments:    Mapped[List["Punishment"]]  = relationship(back_populates="User")
    cases:          Mapped[List["Case"]]        = relationship(back_populates="Case")

class Vote(Base):
    __table_name__ = "Vote"

    id                                          = mapped_column(Uuid, primary_key=True)
    poll_type:      Mapped[enum.Enum]           = mapped_column(Enum(VoteTypeEnum))
    created:        Mapped[datetime.datetime]   = mapped_column(DateTime)
    expired:        Mapped[datetime.datetime]   = mapped_column(DateTime)
    jump_url:       Mapped[str]                 = mapped_column(String(200))
    finished:       Mapped[bool]                = mapped_column(Boolean)
    voter_limited:  Mapped[bool]                = mapped_column(Boolean)
    voters:         Mapped[Optional[List["User"]]]      = mapped_column(ForeignKey("User.id"), nullable=True)
    agree:          Mapped[List["User"]]        = mapped_column(ForeignKey("User.id")) 
    against:        Mapped[List["User"]]        = mapped_column(ForeignKey("User.id")) 
    waiver:         Mapped[List["User"]]        = mapped_column(ForeignKey("User.id"))


class Case(Base):
    __table_name__ = "Case"

    id:             Mapped[uuid.UUID]           = mapped_column(Uuid, primary_key=True)
    created:        Mapped[datetime.datetime]   = mapped_column(DateTime)
    closed:         Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    judges:         Mapped[List["User"]]        = mapped_column(ForeignKey("User.id"))
    appeallees:     Mapped[List["User"]]        = mapped_column(Foreignkey("User.id"))
    appeallors:     Mapped[List["User"]]        = mapped_column(Foreignkey("User.id"))
    step:           Mapped[enum.Enum]           = mapped_column(Enum(CaseStepEnum))
    votes:          Mapped[Optional[List["Vote"]]]      = mapped_column(ForeignKey("Vote.id"), nullable=True)
    completed:      Mapped[bool]                = mapped_column(Boolean)
    punishment:     Mapped["Punishment"]        = mapped_column(ForeignKey("Punishment.id"))
    winner:         Mapped[enum.Enum]           = mapped_column(Enum(CaseWinnerEnum))

class Punishment(Base):
    __table_name__ = "Punishment"

    id:             Mapped[uuid.UUID]           = mapped_column(Uuid, primary_key=True)
    created:        Mapped[datetime.datetime]   = mapped_column(DateTime)
    expired:        Mapped[datetime.datetime]   = mapped_column(DateTime)
    completed:      Mapped[bool]                = mapped_column(Boolean)
    applied:        Mapped[bool]                = mapped_column(Boolean)
    punish_type:    Mapped[enum.Enum]           = mapped_column(Enum(PunishmentTypeEnum))
    authority:      Mapped[enum.Enum]           = mapped_column(Enum(PunishmentAuthorityEnum))
    issued_by:      Mapped[Optional[List["User"]]]      = mapped_column(ForeignKey("User.id"), nullable=True)

class Metadata(Base):
    __table_name__ = "Metadata"

    id:             Mapped[int]                 = mapped_column(Integer, primary_key=True)
    influence_ratio:Mapped[float]               = mapped_column(Float(5))
