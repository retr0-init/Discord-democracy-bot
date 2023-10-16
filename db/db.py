import asyncio
import aiomysql

async def create_db(loop):
    conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                  user='retr0-init', password='',
                                  db='bot_db', loop=loop)
    cur = await conn.cursor()
    with open("build.sql") as f:
        await cur.execute(f.read())
        await cur.close()
        conn.close()
