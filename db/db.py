import asyncio
import aiomysql
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine

from model import User, Vote, Case, Punishment

'''TODO
- Change this to sqlalchemy with sqllite database
- Consider pushing the data insertion and request to a queue to avoid implicit IO
   AsyncSession? https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
'''
async def create_db(loop):
    conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                  user='retr0-init', password='',
                                  db='bot_db', loop=loop)
    cur = await conn.cursor()
    with open("build.sql") as f:
        await cur.execute(f.read())
        await cur.close()
        conn.close()


async def insert_data(table, data):
    # insert the data into a specific table


async def find_data(table, data):
    # Look up the data in the table


async def insert_user(data: dict):
    # Insert the user according to the dict entry
    # {'id':id, 'join_date':join_date, 'roles':[roles], 'punishments':[punishments], 'cases':[cases]}
    # Return Success


async def find_user(user_id: int):
    # Find the user in the database
    # Return bool (user found?), user entry


async def insert_vote(data: dict):
    # Insert the vote according to the dict entry
    '''
    {'id':id, 
     'created':created_date, 'expired':expiry_date, 
     'finished':finished?, 'type':type, 
     'voter_limited':voter_limited?, 'voters':[voters]}
    '''
    # Return Success


async def find_votes():
    # Find all the incompleted votes
    # Return bool (votes found), [votes]


async def insert_case(data: dict):
    # Insert the case (lawsuit) according to the dict entry
    '''
    '''
    # Return success


async def find_cases():
    # Find all the incompleted cases
    # Return bool (cases found), [cases]


async def insert_punishment(data: dict):
    # Insert the punishment according to the dict entry
    '''
    {'id':UUID, 'created':datetime, 'expiry':datetime,
     'type':Enum, 'completed':bool,
     'authority':Enum, 'issued_by':[int]}
    '''
    # Return success


async def find_punishments():
    # Find all the incompleted punishments
    # Return bool (punishments found), [punishments]

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
