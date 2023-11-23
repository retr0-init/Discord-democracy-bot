from __future__ import annotations
import asyncio
import datetime
from typing import List
from typing import Optional
import enum
import uuid

import sqlalchemy

from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ARRAY
from sqlalchemy import Uuid
from sqlalchemy import Enum
from sqlalchemy import UnicodeText
from sqlalchemy import Boolean

from sqlalchemy import CheckConstraint
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

from sqlalchemy.dialects.sqlite import insert

'''TODO
- Check the project folder structure when doing the import
'''
from bot_types_enum import VoteTypeEnum, PunishmentTypeEnum
from bot_types_enum import CaseStepEnum, CaseWinnerEnum, PunishmentAuthorityEnum

class Base(AsyncAttrs, DeclarativeBase):
    pass

class Metadata(Base):
    __tablename__ = "Metadata"

    # id:             Mapped[int]                 = mapped_column(Integer, primary_key=True)
    guild_id:       Mapped[int]                 = mapped_column(Integer, primary_key=True, unique=True)
    influence_ratio:Mapped[float]               = mapped_column(Float(5), default=float(0))
    role_admin:     Mapped[int]                 = mapped_column(Integer, nullable=True)
    role_judge:     Mapped[int]                 = mapped_column(Integer, nullable=True)
    role_wardenry:  Mapped[int]                 = mapped_column(Integer, nullable=True)
    role_technical: Mapped[int]                 = mapped_column(Integer, nullable=True)
    role_propaganda:Mapped[int]                 = mapped_column(Integer, nullable=True)
    role_left:      Mapped[int]                 = mapped_column(Integer, nullable=True)
    role_right:     Mapped[int]                 = mapped_column(Integer, nullable=True)
    role_anarchy:   Mapped[int]                 = mapped_column(Integer, nullable=True)
    role_extreme:   Mapped[int]                 = mapped_column(Integer, nullable=True)
    role_mild:      Mapped[int]                 = mapped_column(Integer, nullable=True)
    ch_election:    Mapped[int]                 = mapped_column(Integer, nullable=True)
    ch_court:       Mapped[int]                 = mapped_column(Integer, nullable=True)
    ch_invite:      Mapped[int]                 = mapped_column(Integer, nullable=True)
    ch_jail:        Mapped[int]                 = mapped_column(Integer, nullable=True)

class DB(object):
    def __init__(self):
        self.engine = create_async_engine("sqlite+aiosqlite:///database.db")
        self.db_metadata = sqlalchemy.MetaData()
        self.async_session = async_sessionmaker(self.engine, expire_on_commit=False)
        pass

    async def init(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def destroy(self):
        await self.engine.dispose()

    async def insert_data(self, table: sa.Table, data: dict) -> bool:
        async with self.async_session() as session:
            await session.execute(
                table.insert(), [data]
            )
            await session.commit()
        return True

    async def upsert(self, table: sa.Table, data: dict):
        insert_stmt = insert(table).values([data])
        print({col: getattr(insert_stmt.excluded, col) for col in data})
        do_update_stmt = insert_stmt.on_conflict_do_update(
            index_where = "guild_id",
            set_ = {col: getattr(insert_stmt.excluded, col) for col in data}
        )
        async with self.async_session() as session:
            await session.execute(do_update_stmt)
            await session.commit()

    async def get_guild_id(self) -> List[int]:
        result = []
        async with self.async_session() as session:
            a = (await session.scalars(select(Metadata))).all()
            for b in a:
                print(b)
                result.append(b.guild_id)
        return result

    async def store_guild_id(self, guild_id: int):
        await self.upsert(Metadata, {"guild_id": guild_id})

    async def upsert_role(self, guild_id: int, role: str, role_id: int):
        await self.upsert(Metadata, {"guild_id": guild_id, f"role_{role.lower()}": role_id})

    async def upsert_channel(self, guild_id: int, channel: str, channel_id: int):
        await self.upsert(Metadata, {"guild_id": guild_id, f"ch_{channel.lower()}": channel_id})

    async def upsert_influence_ratio(self, guild_id: int, influence_ratio: int):
        await self.upsert(Metadata, {"guild_id": guild_id, "influence_ratio": influence_ratio})

    async def get_influence_ratio(self, guild_id: int):
        async with self.async_session() as session:
            result = await session.execute(select(Metadata).where(Metadata.guild_id == guild_id))


db = DB()
