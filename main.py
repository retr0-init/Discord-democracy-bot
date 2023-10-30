import discord
from discord.ext import tasks, commands
import datetime
from uuid import uuid4

from db import db
from user_interface import UIRaiseElection, UINewUserQuestions

'''References
https://programtalk.com/vs4/python/yagomichalak/sloth-bot/main.py/
https://stackoverflow.com/questions/71165431/how-do-i-make-a-working-slash-command-in-discord-py
'''

'''TODO
- [ ] Get the channel and role ID's as setup with setup commands for administrator permission only
- [ ] UI command autocomplete
    - [ ] This should use discord.Client instead. Review its difference from the commands.Bot class
- [ ] command translation with i18n
- [ ] Check the setup command persmissions
'''

bot: discord.ext.commands.Bot = commands.Bot(command_prefix='d!', intents=discord.Intents.all(), help_command=None, case_insensitive=True)

guild_id: int = 0

@bot.event
async def on_ready():
    global guild_id
    # guild_id = await db.get_guild_id()
    await bot.tree.sync(guild=discord.Object(id=guild_id))
    print("Bot is ready!")

@bot.event
async def on_audit_log_entry_create(entry: discord.AuditLogEntry):
    # React if there is a new moderation action is taken
    # Publish that into the "Management Affairs Publish" Channel
    pass

@bot.event
async def on_raw_reaction_add(reaction: discord.RawReactionActionEvent):
    # do something
    pass

@bot.event
async def on_raw_reaction_remove(reaction: discord.RawReactionActionEvent):
    # do something
    pass

@bot.event
async def on_member_join(member: discord.Member):
    guild = member.guild
    if guild.system_channel is not None:
        # Check the user in the database and apply the punishment if so
        pass
    pass

@bot.event
async def on_member_remove(member: discord.Member):
    # Randomly select another member if the quit member is in a case
    pass

@bot.event
async def on_member_update(member: discord.Member):
    # When the role / nickname etc changed
    pass

@bot.event
async def on_message(message: discord.Message):
    message_author = message.author
    if message_author.bot is False:
        # Do something if the message is sent or created
        pass

@bot.command(name="getguildid")
@commands.has_permissions(administrator=True)
@commands.has_any_role('服务器机器人开发')
async def getguildid(ctx:discord.Context):
    global guild_id
    guild_id = await ctx.guild.id
    # await db.store_guild_id(guild_id)

@bot.tree.command(name="setupchannel", description="Setup current channel for specific usage", guild=discord.Object(id=guild_id))
@commands.has_permissions(administrator=True)
@commands.has_any_role('服务器机器人开发')
async def setupchannel(interaction: discord.Interaction, channel_select: str):
    pass

@bot.tree.command(name="setuprole", description="Setup a specific role for specific usage", guild=discord.Object(id=guild_id))
@commands.has_permissions(administrator=True)
@commands.has_any_role('服务器机器人开发')
async def setuprole(interaction: discord.Interaction, role_select: str, role: discord.Role):
    pass

@bot.tree.command(name="punish", description="Issue punishment according to the court conclusion", guild=discord.Object(id=guild_id))
@commands.has_any_role('法官')
async def punish(interaction: discord.Interaction, user_to_ban: discord.Member, time_to_ban: datetime):
    # If this user and the judge are in the case, the judge will have the right to ban the member
    # Or this will be automatically done by the bot
    pass

@bot.tree.command(name="timeout", description="", guild=discord.Object(id=guild_id))
@commands.has_permissions()
@commands.has_any_role('')
async def timeout(interaction: discord.Interaction, user_to_ban: discord.Member):
    # This will count the number of timeout of the member.
    # The time period will change according to the count
    pass

######## UI raising command ########
@bot.tree.command()
@commands.has_any_role('')
async def election(interaction: discord.Interaction):
    await interaction.response.send_modal(UIRaiseElection())

@bot.tree.command()
@commands.has_any_role('')
async def answer(interaction: discord.Interaction, difficulty: str):
    difenum: Optional[UIQuestionDifficultyEnum] = None
    if difficulty.lower() == "easy":
        difenum = UIQuestionDifficultyEnum.Easy
    elif difficulty.lower() == "hard":
        difenum = UIQuestionDifficultyEnum.Hard

    if difenum is not None:
        await interaction.response.send_message(ephemeral=True, view=UINewUserQuestions(difenum))
    else:
        await interaction.response.send_message(ephemeral=True, content="Please enter the proper difficulty setting!")

if __name__ == "__main__":
    pass
