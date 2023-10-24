import discord
from discord.ext import tasks, commands
import datetime
from uuid import uuid4

'''References
https://programtalk.com/vs4/python/yagomichalak/sloth-bot/main.py/
'''

bot = commands.Bot(command_prefix='d!', intents=discord.Intents.all(), help_command=None, case_insensitive=True)

@bot.event
async def on_ready():
    print("Bot is ready!")

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

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_raw_reaction_add(self, reaction: discord.RawReactionActionEvent):
        # do something

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_raw_reaction_remove(self, reaction: discord.RawReactionActionEvent):
        # do something

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        if guild.system_channel is not None:
            # Check the user in the database and apply the punishment if so
            pass
        pass

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_member_remove(self, member: discord.Member):
        # Randomly select another member if the quit member is in a case
        pass

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_member_update(self, member: discord.Member):
        # When the role / nickname etc changed
        pass

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_message(self, message: discord.Message):
        message_author = message.author
        if message_author.bot is False:
            # Do something if the message is sent or created
            pass

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_audit_log_entry_create(self, entry: discord.AuditLogEntry):
        # React if there is a new moderation action is taken
        # Publish that into the "Management Affairs Publish" Channel
        pass


if __name__ == "__main__":
    pass
