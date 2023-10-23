import asyncio
import aiosqlite
import sqlalchemy as sa
from sqlalchemy.orm import Relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from model import User, Vote, Case, Punishment, Metadata

from datatime import datatime
from typing import List
import uuid
from bot_types_enum import VoteTypeEnum, CaseStepEnum, CaseWinnerEnum, PunishmentTypeEnum, PunishmentAuthorityEnum

'''TODO
- [ ] Change this to sqlalchemy with sqllite database
- [ ] Error handling for async database operations
- [ ] Find whether there are more find functions needed
    - [ ] "Upsert" instead of "insert"
- [ ] Table creation if not exist
- [ ] Table & field conflict resolve
- [x] Consider pushing the data insertion and request to a queue to avoid implicit IO
   AsyncSession? https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
'''
class DB(Object):
    async def __init__(self):
        self.engine = await create_async_engine("sqlite+aiosqlite:///database.db")

    async def insert_data(self, table: sa.Table, data: dict) -> bool:
        async with self.engine.connect() as conn:
            await conn.execute(
                table.insert(), [data]
            )
        return True

    async def find_user_byid(self, user_id: int) -> sa.CursorResult:
        async with self.engine.connect() as conn:
            result = await conn.execute(sa.select(User.c.id == user_id))
        return result

    async def insert_user(self, id_: int, join_date: datetime, roles: List[int] = []) -> bool:
        await self.insert_data(User, {"id": id_, "join_date": join_date, "roles": roles, "punishments": [], "cases": []})
        return True

    async def insert_vote(self, poll_type: VoteTypeEnum, created: datetime, expired: datetime, message_id: int, jump_url: str
                          voter_limited: bool = False, voters: List[int] = []) -> bool, uuid.UUID, str:
        id_ = uuid.uuid4()
        await self.insert_data(Vote, {
            "id":           id_,
            "poll_type":    poll_type,
            "created":      created,
            "expired":      expired,
            "jump_url":     jump_url,
            "voter_limited":voter_limited,
            "voters":       voters,
            "agree":        [],
            "against":      [],
            "waiver":       []
        })
        return True, id_, jump_url

    async def find_vote_bymessageid(self, message_id: int) -> sa.CursorResult:
        async with self.engine.connect() as conn:
            result = await conn.execute(sa.select(Vote.c.message_id == message_id))
        return result

    async def insert_case(self, created: datetime, , message_id: int, jump_url: str,
                          judges: List[int], appeallees: List[int], appeallors: List[int],
                          step: CaseStepEnum, closed: datetime = None) -> bool, uuid.UUID, str:
        id_ = uuid.uuid4()
        data = {
            "id":           id_,
            "created":      created,
            "message_id":   message_id,
            "jump_url":     jump_url,
            "judges":       judges,
            "appeallees":   appeallees,
            "appeallors":   appeallors,
            "step":         step,
            "completed":    False,
            "punishment":   [],
            "winner":       CaseWinnerEnum.NotDetermined
        }
        if closed is not None:
            data["closed"] = closed
        await self.insert_data(Case, data)
        return True, id_, jump_url

    async def find_case_bymessageid(self, message_id: int) -> sa.CursorResult:
        async with self.engine.connect() as conn:
            result = await conn.execute(sa.select(Case.c.message_id == message_id))
        return result

    async def find_case_incompleted_byexpired(self, expired: datetime) -> sa.CursorResult:
        async with self.engine.connect() as conn:
            results = await conn.execute(sa.select(Case.c.expired <= expired and Case.c.completed is False))

    async def insert_punishment(self, created: datetime, expired: datetime, punish_type: PunishmentTypeEnum,
                            authority: PunishmentAuthorityEnum, issued_by: list = []) -> bool, uuid.UUID:
        id_ = uuid.uuid4()
        await self.insert_data(Punishment, {
            "id":           id_,
            "created":      created,
            "expired":      expired,
            "completed":    False,
            "applied":      False,
            "punish_type":  punish_type,
            "authority":    authority,
            "issued_by":    issued_by
        })
        return True, id_

    async def find_punishments_incompleted_byexpired(self, expired: datetime) -> sa.CursorResult:
        async with self.engine.connect() as conn:
            results = await conn.execute(sa.select(Punishment.c.expired <= expired and Punishment.c.completed is False))
        return results

    async def find_punishments_incompleted_notapplied_byexpired(self, expired: datetime) -> sa.CursorResult:
        async with self.engine.connect() as conn:
            results = await conn.execute(sa.select(Punishment.c.expired <= expired and Punishment.c.completed is False and Punishment.c.applied is False))
        return results


'''TODO
Move this to the discord event trigger code block
'''
'''
async def add_user(id: int):
    # Look for the user id in database
    # if the user is in the database
    # # The user rejoins the server, re-apply the roles and punishments.
    # else 
    # # Add the user in the database with join date and the other fields init
'''
