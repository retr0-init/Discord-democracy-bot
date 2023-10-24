import discord
import traceback

from typing import List, Optional
from bot_types_enum import VoteTypeEnum, PunishmentTypeEnum, CaseStepEnum, CaseWinnerEnum, PunishmentAuthorityEnum


'''TODO
- [ ] Create the UI for election, court, normal voting, and moderation
- [ ] UIElection needs to have choice filter based on previous selection
- [ ] RoleSelect and ChannelSelect, specific selections
    - [ ] Or use Select only and map the choice to the specific channel
- [ ] UIVote needs to send the message to convert it to view. Need to check how to do it properly.
- [ ] UIVote manage vote according to the inputs and results
'''


class UIRaiseElection(discord.ui.Modal, title="Raise an election"):
    #TODO Will the electable roles all be created individually?

    @discord.ui.select(
        cls = discord.ui.RoleSelect,
        options = [
            discord.Role(), # Role Admin
            discord.Role(), # Role Judge
            discord.Role(), # Role Technical
            discord.Role()  # Role Wardenry
        ],
        placeholder = "Please select the role you want to be elected"
    )
    async def select_role(self, interaction: discord.Interaction, select_item: discord.RoleSelect):
        pass

    @discord.ui.select(
        cls = discord.ui.ChannelSelect,
        options = [
            discord.Channel(),  # Channel Left
            discord.Channel(),  # Channel Right
            discord.Channel(),  # Channel Anarchy
            discord.Channel(),  # Channel Mild
            discord.Channel()   # Channel Extreme
        ],
        placeholder = "Please select the channel where you will be elected as an admin",
        channel_types = [discord.ChannelType.text]
    )
    async def select_channel(self, interaction: discord.Interaction, select_item: discord.ChannelSelect):
        pass

    election_abstract = discord.ui.TextInput(
        label = "What is your election abstract?",
        style = discord.TextStyle.long,
        placeholder = "Enter your election abstract here...",
        required = True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Thanks for participating election, {self.name.value}!", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message("Oops! Something went wrong. Please check the information enterred.", ephemeral=True)
        traceback.print_exception(type(error), error, error.__traceback__)


class UIRaiseVoting(discord.ui.Modal, title="Raise a vote"):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Select(
            options = [
                discord.SelectOption(label="Normal",        value="Normal"),
                discord.SelectOption(label="Guild Affairs", value="Guild Affairs"),
                discord.SelectOption(label="Institution",   value="Institution"),
                discord.SelectOption(label="Law",           value="Law")
            ],
            placeholder = "Please select the type of this vote"
        ))
        self.add_item(discord.ui.TextInput(
            label = "What is the question of your raised vote?",
            placeholder = "Enter your vote question here...",
            required = True
        ))

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Thanks for submitting your vote, {self.name.value}", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message("Oops! Something went wrong. Please check the information enterred.", ephemeral=True)
        traceback.print_exception(type(error), error, error.__traceback__)
    pass

class UIVoting(discord.ui.View):
    async def __new__(self, vote_title: str, vote_body: str, options: List[str], vote_type: VoteTypeEnum, timeout: float):
        match vote_type:
            case VoteTypeEnum.LegislationConstitution:
                author = "Legislation Constitution"
                colour = discord.Colour.from_str("#0000FF")
            case VoteTypeEnum.LegislationLaw:
                author = "Legislation Law"
                colour = discord.Colour.from_str("#6666FF")
            case VoteTypeEnum.LegislationAffair:
                author = "Legislation Affair"
                colour = discord.Colour.from_str("#CCCCFF")
            case VoteTypeEnum.Justice:
                author = "Justice"
                colour = discord.Colour.from_str("#EED202")
            case VoteTypeEnum.ElectionJudge:
                author = "Judge Election"
                colour = discord.Colour.from_str("#0066CC")
            case VoteTypeEnum.ElectionAdmin:
                author = "Admin Election"
                colour = discord.Colour.from_str("#6600CC")
            case VoteTypeEnum.ElectionWardenry:
                author = "Wardenry Election"
                colour = discord.Colour.from_str("#606060")
            case VoteTypeEnum.Impeachment:
                author = "Impeachment"
                colour = discord.Colour.from_str("#FF0000")
            case VoteTypeEnum.Invite:
                author = "New member vote"
                colour = discord.Colour.from_str("#00FF00")
        msg = discord.Embed(
            title = f"{vote_title}",
            author = author,
            description = f"{vote_body}",
            colour = colour
        )
        '''Send the message and convert it to self
        message = await ctx.send_message(embed=msg)
        return discord.ui.View.from_message(message, timeout=timeout)
        '''

    async def __init__(self, vote_title: str, vote_body: str, options: List[str], vote_type: VoteTypeEnum, timeout: float):
        # super().__init__(timeout=timeout)
        self.vote_type : VoteTypeEnum = vote_type
        self.vote_title : str = vote_title
        self.vote_body : str = vote_body
        self.vote_options : str = options

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        pass

    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    async def on_timeout(self) -> None:
        await self.message.channel.send("Time Out")
        await self.disable_all_items()
        # Then make the result from the voting result
