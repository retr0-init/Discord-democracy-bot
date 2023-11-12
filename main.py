import discord
from discord.ext import tasks, commands
import datetime
from uuid import uuid4

#from db import DB
from user_interface import UIRaiseElection, UINewUserQuestions, UIControlPanel

TOKEN: str = "MTE1OTIyODAyNTA4MzI2OTIxMQ.GVI86N.z2uzJKkxEulUsXcol7eOZ40RpwODHw6XGhBYtk"

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
- [ ] News / Information source from public funded broadcasters
    - BBC Zhongwen "https://feeds.bbci.co.uk/zhongwen/simp/rss.xml"
    - ABC Zhongwen "https://www.abc.net.au/news/feed/8537074/rss_fulltext.xml"
    - PBS World "https://www.pbs.org/newshour/feeds/rss/world"
    - PBS US Politics "https://www.pbs.org/newshour/feeds/rss/politics"
    - PBS US Economy "https://www.pbs.org/newshour/feeds/rss/economy"
    - PBS podcasts "https://www.pbs.org/newshour/feeds/rss/podcasts"
    - Swiss Info Chinese "https://www.swissinfo.ch/chi"
    - ... https://www.swissinfo.ch/chi/%E4%B8%AD%E5%9B%BD%E5%A6%82%E4%BD%95%E6%94%B9%E5%86%99%E4%BA%BA%E6%9D%83%E5%87%86%E5%88%99/48842062
    - PTS "https://news.pts.org.tw/xml/newsfeed.xml"
    - KBS International Chinese "http://world.kbs.co.kr/rss/rss_news.htm?lang=c&id=In"
    - CBC World "https://www.cbc.ca/webfeed/rss/rss-world"
- [ ] Bot Tree command context menu?
- [ ] Bot Tree command autocomplete
'''

bot: discord.ext.commands.Bot = commands.Bot(command_prefix='d!', intents=discord.Intents.all(), help_command=None, case_insensitive=True)

guild_id: int = 1156709757625835681


db = None

@bot.event
async def on_ready():
    global guild_id
    global db
    # guild_id = await db.get_guild_id()
    await bot.tree.sync(guild=discord.Object(id=guild_id))
    # db = await DB()
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

@bot.tree.command(name="getguildid")
@commands.has_permissions(administrator=True)
@commands.has_any_role('服务器机器人开发')
async def getguildid(interaction: discord.Interaction):
    global guild_id
    guild_id = interaction.guild.id
    # await db.store_guild_id(guild_id)
    await interaction.response.send_message(content=f"The Guild ID for {interaction.guild.name} has been set!", ephemeral=True)

@bot.tree.command(name="setupchannel", description="Setup current channel for specific usage", guild=discord.Object(id=guild_id))
@commands.has_permissions(administrator=True)
@commands.has_any_role('服务器机器人开发')
async def setupchannel(interaction: discord.Interaction, channel_select: str):
    channel: Union[discord.abc.GuildChannel, discord.Thread] = interaction.channel
    channel_id: int = 0
    stored: bool = False
    if isinstance(channel, discord.Thread):
        channel_id = channel.parent_id
    elif isinstance(channel, discord.abc.GuildChannel):
        channel_id = channel.id
    else:
        print("This channel is not for guilds!")
    if channel_select in CHANNEL_ID_LIST.keys():
        CHANNEL_ID_LIST[channel_select] = channel_id
        stored = True
    if stored and channel_id != 0:
        await interaction.response.send_message(content=f"The channel ID for {channel_select} has been updated!", ephemeral=True)
    else:
        await interaction.response.send_message(content=f"ERROR: The channel ID for {channel_select} update failed!", ephemeral=True)

@bot.tree.command(name="setuprole", description="Setup a specific role for specific usage", guild=discord.Object(id=guild_id))
@commands.has_permissions(administrator=True)
@commands.has_any_role('服务器机器人开发')
async def setuprole(interaction: discord.Interaction, role_select: str, role: discord.Role):
    stored: bool = False
    if role_select in ROLE_ID_LIST.keys():
        ROLE_ID_LIST[role_select] = role.id
        await interaction.response.send_message(content=f"SUCCESS: Role {role.name} is set as {role_select}!", ephemeral=True)
    else:
        await interaction.response.send_message(content=f"ERROR: Role {role_select} does not exist!", ephemeral=True)

@bot.tree.command(name="punish", description="Issue punishment according to the court conclusion", guild=discord.Object(id=guild_id))
@commands.has_any_role('法官')
async def punish(interaction: discord.Interaction, user_to_ban: discord.Member, time_to_ban: int):
    # If this user and the judge are in the case, the judge will have the right to ban the member
    # Or this will be automatically done by the bot
    pass
'''
@bot.tree.command(name="timeout", description="", guild=discord.Object(id=guild_id))
@commands.has_permissions()
@commands.has_any_role('')
async def timeout(interaction: discord.Interaction, user_to_ban: discord.Member):
    # This will count the number of timeout of the member.
    # The time period will change according to the count
    pass
'''
######## UI raising command ########
@bot.tree.command(name="callbot", description="Raise Bot UI", guild=discord.Object(id=guild_id))
async def callbotUI(interaction: discord.Interaction):
    await interaction.response.send_message(content=f"Please choose the action you want to take by pressing one of the button below:", view=UIControlPanel(interaction.user), ephemeral=True)

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
    bot.run(TOKEN)
