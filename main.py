import discord
from discord.ext import tasks, commands

class BotLoopCog(commands.Cog):
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

    @tasks.loop(seconds=60.0)
    async def monitorLoop(self):
        pass

if __name__ == "__main__":
    pass
