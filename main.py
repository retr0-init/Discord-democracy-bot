import discord
from discord.ext import tasks, commands
import datetime
from uuid import uuid4

class BotDemocracyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.index = 0
        self.databaseLoop.start()
        self.monitorLoop.start()

    def cog_unload(self):
        self.databaseLoop.cancel()
        self.monitorLoop.cancel()

    @tasks.loop(seconds=60.0)
    async def databaseLoop(self):
        print("running {}".format(self.index))
        self.index += 1
        return

    @databaseLoop.before_loop
    async def before_databaseLoop(self):
        await self.bot.wait_until_ready()
        # This should wait for the database connection complete
        return

    @databaseLoop.after_loop
    async def on_databaseLoop_cancel(self):
        return

    @tasks.loop(seconds=60.0)
    async def monitorLoop(self):
        return

    @monitorLoop.before_loop
    async def before_monitorLoop(self):
        await self.bot.wait_until_ready()

    @monitorLoop.after_loop
    async def on_monitorLoop_cancel(self):
        return


if __name__ == "__main__":
    pass
