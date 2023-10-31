import discord
import traceback
import os

import uuid
import datetime
from typing import List, Optional, Dict, Union
from bot_types_enum import VoteTypeEnum, PunishmentTypeEnum, CaseStepEnum,
                            CaseWinnerEnum, PunishmentAuthorityEnum, UIVotingButtonEnum,
                            UIQuestionDifficultyEnum
from main import ROLE_ID_LIST, CHANNEL_ID_LIST

'''TODO
- [ ] Create the UI for election, court, normal voting, and moderation
- [ ] UIElection needs to have choice filter based on previous selection
- [x] Or use Select only and map the choice to the specific channel
- [x] UIVote needs to send the message to convert it to view. Need to check how to do it properly.
- [ ] UIVote manage vote according to the inputs and results
'''


class UIRaiseElection(discord.ui.Modal, title="Raise an election"):
    #TODO Will the electable roles all be created individually?
    '''
    Choose the role and channel according to the literal option.
    '''

    @discord.ui.select(
        cls = discord.ui.RoleSelect,
        options = [
            discord.SelectOption(label="Admin",     value="Admin"),     # Role Admin
            discord.SelectOption(label="Judge",     value="Judge"),     # Role Judge
            discord.SelectOption(label="Technical", value="Technical"), # Role Technical
            discord.SelectOption(label="Wardenry",  value="Wardenry")   # ardenry
        ],
        placeholder = "Please select the role you want to be elected"
    )
    async def select_role(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        selected_option : str = select_item.values[0]
        selected_role : Optional[discord.Role] = None
        selected_role = interaction.guild.get_role(ROLE_ID_LIST[selected_option])
        if selected_option == "Admin":
            # Need to get the Role ID of Admin
            pass
        elif selected_option == "Judge":
            pass
        elif selected_option == "Technical":
            pass
        elif selected_option == "Wardenrey":
            pass
        else:
            # Handle error selection
        pass

    @discord.ui.select(
        cls = discord.ui.ChannelSelect,
        options = [
            discord.SelectOption(label="Left",      value="Left"),      # Channel Left
            discord.SelectOption(label="Right",     value="Right"),     # Channel Left
            discord.SelectOption(label="Anarchy",   value="Anarchy"),   # Channel Left
            discord.SelectOption(label="Mild",      value="Mild"),      # Channel Left
            discord.SelectOption(label="Extreme",   value="Extreme")    # Channel Left
        ],
        placeholder = "Please select the channel where you will be elected as an admin",
        channel_types = [discord.ChannelType.text]
    )
    async def select_channel(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        selected_option : str = select_item.values[0]
        selected_channel : Optional[discord.Channel] = None
        if selected_option == "Left":
            # Need to get the role ID of Left
        elif selected_option == "Right":
            pass
        elif selected_option == "Anarchy":
            pass
        elif selected_option == "Mild":
            pass
        elif selected_option == "Extreme":
            pass
        else:
            # Handle the error selection
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

class UIVotingButton(discord.ui.Button):
    def __init__(self, label: str, button_type: UIVotingButtonEnum, custom_id: str, row: Optional[int] = None):
        match button_type:
            case UIVotingButtonEnum.Agree:
                style = discord.ButtonStyle.success
            case UIVotingButtonEnum.Against:
                style = discord.ButtonStyle.danger
            case UIVotingButtonEnum.Waiver:
                style = discord.ButtonStyle.primary
            case _:
                e = Exception("The voting button type does not match")
                traceback.print_exception(type(e), e, e.__traceback__)
                style = discord.ButtonStyle.grey
        super().__init__(label=label, style=style, custom_id=custom_id, row=row)

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: UIVoting = self.view
        buttons = view.buttons
        vote_type: VoteTypeEnum = view.vote_type
        user: Union[discord.User, discord.Member] = interaction.user
        # TODO check user permission with the database check
        # TODO disable the button for this interaction user

class UIVoting(discord.ui.View):
    '''
    Pass the title, body and vote_type to the command reply, and pass the message object to this class
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
        #Send the message and convert it to self
        message = await ctx.send_message(embed=msg)
        return discord.ui.View.from_message(message, timeout=timeout)
    '''
    
    id: uuid.UUID
    created: datetime.datetime
    expired: datetime.datetime
    finished: bool
    vote_type: VoteTypeEnum
    voter_limited: bool
    voters: Optional[List[Union[discord.User, discord.Member]]]
    agree: List[Union[discord.User, discord.Member]]
    against: List[Union[discord.User, discord.Member]]
    waiver: List[Union[discord.User, discord.Member]]
    jump_url: str
    buttons: List[UIVotingButton] = []

    async def __new__(self, message: discord.Message, vote_type: VoteTypeEnum, timeout: float):
        return discord.ui.View.from_message(message, timeout=timeout)

    async def __init__(self, message: discord.Messgae, vote_type: VoteTypeEnum, timeout: float):
        # super().__init__(timeout=timeout)
        self.vote_type : VoteTypeEnum = vote_type

        for vote_option in UIVotingButtonEnum:
            label = vote_option.value
            button = UIVotingButton(label=label, button_type=vote_option, custom_id=label, row=2)
            self.buttons.append(button)
            self.add_item(button)

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

class UINewUserQuestions(discord.ui.View):
    async def __init__(self, difficulty: UIQuestionDifficultyEnum):
        # Load questions
        '''Question list format example
        [
            {
                "UUID":     "123iudhfjkey54-1234rueiy2sdf",
                "Question": "1+1 equals to...",
                "Choices":  {
                                'A': '2',
                                'B': '1',
                                'C': '0'.
                                'D': '-2'
                            },
                "Answer":   'A'
            },
            ...
        ]
        '''
        questions: List[Dict[str, Union[uuid.UUID, str, Dict[str, str], str]]] = await db.get_questions(difficulty)
        # Randomise questions?
        '''Optional
        - [ ] Randomise the question list
        - [ ] Randomise the choices of each question
        '''
        # TODO

        for question in questions:
            self.add_item(discord.ui.Select(
                custom_id = question["UUID"],
                options = [discord.SelectOption(label=dictin[key], value=key) for key in dictin],
                placeholder = question["Question"]
            ))
        
        '''TODO
        - [ ] Add callback to the buttons
        '''
        self.add_item(discord.ui.Button(label="Submit", style=discord.ButtonStyle.success))
        self.add_item(discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger))
