import discord
import traceback
import os

import uuid
import datetime
from typing import List, Optional, Dict, Union
from bot_types_enum import (VoteTypeEnum, PunishmentTypeEnum, CaseStepEnum,
                            CaseWinnerEnum, PunishmentAuthorityEnum, UIVotingButtonEnum,
                            UIQuestionDifficultyEnum)
from metadata import ROLE_ID_LIST, CHANNEL_ID_LIST, ROLE_ROLE_LIST

'''TODO
- [ ] Create the UI for election, court, normal voting, and moderation
- [x] UIElection needs to have choice filter based on previous selection
- [x] Or use Select only and map the choice to the specific channel
- [x] UIVote needs to send the message to convert it to view. Need to check how to do it properly.
- [x] UIVote manage vote according to the inputs and results
- [x] UIRaiseElection: show channel selection after the role selection
- [x] UIVoting: Update the UI view for the voting interface
- [x] Update the UI class that calls the UIVoting class.
- [ ] Update the database from the UIVoting class
- [x] Think about the Button implementation for the UIVoting class
- [x] Finish the Result Embed generation method
- [ ] Finish the invite question pass determination method 
- [ ] Automatically give role based on vote result and vote raise
- [ ] Replace the technical admin position to propaganda admin
'''

class UIRaiseElectionElectionAbstract(discord.ui.Modal):

    election_abstract = discord.ui.TextInput(
        label = "What is your election abstract?",
        style = discord.TextStyle.long,
        placeholder = "Enter your election abstract here...",
        required = True
    )

    def __init__(self, selected_role: str, author: discord.Member):
        self.electoral: str = list(ROLE_ID_LIST.keys())[list(ROLE_ID_LIST.value()).index(author.role.id)]
        title = f"{selected_role}{f' in {electoral} electorals' if selected_role == 'Admin' or selected_role == 'Judge' else ''}"
        super().__init__(title=title)
        self.selected_role      : str = selected_role
        self.selected_channel   : str = self.electoral

    async def on_submit(self, interaction: discord.Interaction):
        guild : discord.Guild = interaction.guild
        channel : discord.Role = guild.get_role(ROLE_ID_LIST[self.selected_role])
        role: discord.Role = guild.get_role(ROLE_ID_LIST[self.selected_channel])
        election_channel : discord.Channel = await guild.fetch_channel(CHANNEL_ID_LIST["Election"])
        #TODO complete the class init and method's parameters
        #TODO complete the election thread title and body
        #TODO add this voting to the database? Do it in the UIVoting class?
        embed = UIVoting.generate_embed()
        if self.selected_role == "Admin":
            vote_type: VoteTypeEnum = VoteTypeEnum.ElectionAdmin
        elif self.selected_role == "Judge":
            vote_type: VoteTypeEnum = VoteTypeEnum.ElectionJudge
        elif self.selected_role == "Wardenry":
            vote_type: VoteTypeEnum = VoteTypeEnum.ElectionWardenry
        elif self.selected_role == "Tecchnical":
            vote_type: VoteTypeEnum = VoteTypeEnum.ElectionTechnical
        view: discord.View = UIVoting(vote_type=vote_type, author=interaction.user, timeout=604800.0)
        view.thread, view.message = await election_channel.create_thread(
            name="title",                       # Election vote title
            content="body",                     # Plain text body. Perbably not required.
            embed=discord.Embed(),              # Rich text body 
            view=view,                          # voting button view 
            reason=f"Created Election - {self.selected_role_str}",
            slowmode_delay=1,                   # slow mode delay for 1 second
            applied_tags=[],
            auto_archive_duration=1440          # Auto archived period. Must be 1 hour (60), 1 day (1440), 3 days (4320) or 7 days (10080)
        )
        await interaction.response.edit_message(content=f"Thanks for participating the election as {self.selected_role}! Your election proposal has been sent to the election channel.", view=None)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message("Oops! Something went wrong. Please check the information enterred.", ephemeral=True)
        traceback.print_exception(type(error), error, error.__traceback__)


class UIRaiseElection(discord.ui.View):
    #TODO Will the electable roles all be created individually?
    def __init__(self, author: discord.Member):
        super().__init__()
        self.author: discord.Member = author
        role_id: List[int] = [i.id for i in self.author.roles]
        if ROLE_ID_LIST['Left'] in role_id or ROLE_ID_LIST['Right'] in role_id or ROLE_ID_LIST['Extreme'] in role_id or ROLE_ID_LIST['Mild'] in role_id or ROLE_ID_LIST['Anarchy'] in role_id:
            pass
        else:
            print("You need to chooose the electorate tag first!")
    '''
    Choose the role and channel according to the literal option.
    '''
    @discord.ui.select(
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
        self.selected_role_str : str = selected_option
        await interaction.response.send_modal(modal=UIRaiseElectionElectionAbstract(selected_role_str, self.author))
    



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
    def __init__(self, label: str, button_type: UIVotingButtonEnum, custom_id: str, vote_type: VoteTypeEnum, all_lists: Dict[str, List[Union[discord.user, discord.Member]]], row: Optional[int] = None):
        self.vote_type: VoteTypeEnum = vote_type
        self.users: List[discord.Member] = all_lists[button_type.value]
        self.all_user_lists: Dict[str, List[discord.Member]] = all_lists
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
        list_bool: List[bool] = [user in x for x in self.all_user_lists]
        if not any(list_bool):
            self.users.append(user)
            await interaction.response.send_message(content=f"You voted as {self.vote_type.value}", ephemeral=True)
        else:
            await interaction.response.send_message(content=f"You have already voted for {list(self.all_user_lists.keys())[list_bool.index(True)]}!", ephemeral=True)
        # TODO check user permission with the database check
        await self.customCallback(interaction)

    async def customCallback(self, interaction: discord.Interaction):
        pass

class UIVoting(discord.ui.View):
    
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
    clicked_users: List[int] = []

    colour: List[Optional[discord.Colour]] = [None]
    # https://stackoverflow.com/questions/69265909/discord-py-edit-the-interaction-message-after-a-timeout-in-discord-ui-select
    message: Optional[discord.Message] = None
    thread: Optional[discord.Thread] = None


    async def __init__(self, vote_type: VoteTypeEnum, author: discord.Member, timeout: float = 604800.0):
        '''
        Default timeout of this is 7 days. Need to specify the date to be 3 days later (if the vote influence ratio is 0)
        '''
        super().__init__(timeout=timeout)
        self.vote_dict: Dict[str, List[Union[discord.Member, discord.User]]] = {
            "Agree":    self.agree,
            "Against":  self.against,
            "Waiver":   self.waiver
        }
        self.author = author
        self.vote_type : VoteTypeEnum = vote_type

        for vote_option in UIVotingButtonEnum:
            label = vote_option.value
            button = UIVotingButton(label=label, button_type=vote_option, custom_id=label, all_lists=self.vote_dict, row=2)
            self.buttons.append(button)
            self.add_item(button)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        pass

    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)
        await self.stop()

    def determine_vote_pass(self) -> bool:
        return len(self.agree) - len(self.against) >= 30

    async def on_timeout(self) -> None:
        await self.message.channel.send(f"Time Out. The result of this vote is {'PASS' if self.determine_vote_pass() else 'NOT PASS'}. This thread will be archived and locked.")
        await self.disable_all_items()
        await self.thread.edit(archived=True, locked=True, reason="The Vote completes. The thread is archived and locked.")
        name: str = ""
        content: str = ""
        embed: discord.Embed = discord.Embed()
        reason: str = ""
        match self.vote_type:
            case VoteTypeEnum.ElectionJudge:
                if self.determine_vote_pass():
                    given_role: discord.Role = self.message.guild.get_role(ROLE_ID_LIST["Judge"])
                    await self.author.add_roles([given_role], reason = "Election completed. Judge role added to {}.".format(self.author.display_name))
                name: str = f"{self.author.display_name} is {'' if self.determine_vote_pass() else 'NOT '}elected as Judge."
                content: str = f"Judge Election completes. The result is:"
                embed: discord.Embed = discord.Embed(
                    description = f"# Decision: @{self.author.mention} is {'NOT ' if not self.determine_vote_pass() else ''}elected as Judge.\n## Agree: {len(self.agree)}\n## Disagree: {len(self.against)}\n## Waiver: {len(self.waiver)}",
                    timestamp = datetime.datetime.now()
                )
                reason = "Election Judge result is published."
            case VoteTypeEnum.ElectionAdmin:
                if self.determine_vote_pass():
                    given_role: discord.Role = self.message.guild.get_role(ROLE_ID_LIST["Admin"])
                    await self.author.add_roles([given_role], reason = "Election completed. Admin role added to {}.".format(self.author.display_name))
                name: str = f"{self.author.display_name} is elected as Admin."
                content: str = f"Admin Election completes. The result is:"
                embed: discord.Embed = discord.Embed(
                    description = f"# Decision: @{self.author.mention} is {'NOT ' if not self.determine_vote_pass() else ''}elected as Admin.\n## Agree: {len(self.agree)}\n## Disagree: {len(self.against)}\n## Waiver: {len(self.waiver)}",
                    timestamp = datetime.datetime.now()
                )
                reason = "Election Admin result is published."
            case VoteTypeEnum.ElectionWardenry:
                if self.determine_vote_pass():
                    given_role: discord.Role = self.message.guild.get_role(ROLE_ID_LIST["Wardenry"])
                    await self.author.add_roles([given_role], reason = "Election completed. Wardenry role added to {}.".format(self.author.display_name))
                name: str = f"{self.author.display_name} is elected as Wardenry."
                content: str = f"Wardenry Election completes. The result is:"
                embed: discord.Embed = discord.Embed(
                    description = f"# Decision: @{self.author.mention} is {'NOT ' if not self.determine_vote_pass() else ''}elected as Wardenry.\n## Agree: {len(self.agree)}\n## Disagree: {len(self.against)}\n## Waiver: {len(self.waiver)}",
                    timestamp = datetime.datetime.now()
                )
                reason = "Election Wardenry result is published."
            case VoteTypeEnum.ElectionTechnical:
                if self.determine_vote_pass():
                    given_role: discord.Role = self.message.guild.get_role(ROLE_ID_LIST["Technical"])
                    await self.author.add_roles([given_role], reason = "Election completed. Technical role added to {}.".format(self.author.display_name))
                name: str = f"{self.author.display_name} is elected as Technical."
                content: str = f"Technical Election completes. The result is:"
                embed: discord.Embed = discord.Embed(
                    description = f"# Decision: @{self.author.mention} is {'NOT ' if not self.determine_vote_pass() else ''}elected as Technical.\n## Agree: {len(self.agree)}\n## Disagree: {len(self.against)}\n## Waiver: {len(self.waiver)}",
                    timestamp = datetime.datetime.now()
                )
                reason = "Election Technical result is published."
        channelPublish: discord.Channel = await self.message.guild.fetch_channel(CHANNEL_ID_LIST["Publish"])
        await channelPublish.create_thread(
            name = name,
            content = "",
            embed = embed,
            reason = reason,
            applied_tags = [],
            file = discord.File()
        )
        # Then make the result from the voting result

    @staticmethod
    def determine_colour(vote_type: VoteTypeEnum) -> discord.Colour:
        match vote_type:
            case VoteTypeEnum.LegislationConstitution:
                colour = discord.Colour.from_str("#0000FF")
            case VoteTypeEnum.LegislationLaw:
                colour = discord.Colour.from_str("#6666FF")
            case VoteTypeEnum.LegislationAffair:
                colour = discord.Colour.from_str("#CCCCFF")
            case VoteTypeEnum.Justice:
                colour = discord.Colour.from_str("#EED202")
            case VoteTypeEnum.ElectionJudge:
                colour = discord.Colour.from_str("#0066CC")
            case VoteTypeEnum.ElectionAdmin:
                colour = discord.Colour.from_str("#6600CC")
            case VoteTypeEnum.ElectionWardenry:
                colour = discord.Colour.from_str("#606060")
            case VoteTypeEnum.ElectionTechnical:
                colour = discord.Colour.from_str("#66CC00")
            case VoteTypeEnum.Impeachment:
                colour = discord.Colour.from_str("#FF0000")
            case VoteTypeEnum.Invite:
                colour = discord.Colour.from_str("#00FF00")
            case _:
                colour = discord.Colour.dark_grey

        return colour

    @staticmethod
    def generate_embed(vote_type: VoteTypeEnum, vote_author: discord.Member, vote_message: str, member_against: Optional[discord.Member]) -> Optional[discord.Embed]:
        colour : discord.Colour = discord.Colour.light_grey
        author : str = "Invalid"
        title  : str = "Invalid"
        current_time: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
        zettlekasten_tag: str = current_time.strftime("%Y%m%d%H%M%S")
        match vote_type:
            case VoteTypeEnum.LegislationConstitution:
                author = "Legislation Constitution"
                colour = discord.Colour.from_str("#0000FF")
                title = f"{zettlekasten_tag} Constitution Vote"
            case VoteTypeEnum.LegislationLaw:
                author = "Legislation Law"
                colour = discord.Colour.from_str("#6666FF")
                title = f"{zettlekasten_tag} Regional Law Vote"
            case VoteTypeEnum.LegislationAffair:
                author = "Legislation Affair"
                colour = discord.Colour.from_str("#CCCCFF")
                title = f"{zettlekasten_tag} Guild Affair Vote"
            case VoteTypeEnum.Justice:
                if member_against is None:
                    print("The member to against is not provided!")
                    return None
                author = "Justice"
                colour = discord.Colour.from_str("#EED202")
                title = f"{zettlekasten_tag} Justice {vote_author.guild.name} V.s. {member_against.display_name}"
            case VoteTypeEnum.ElectionJudge:
                author = "Judge Election"
                colour = discord.Colour.from_str("#0066CC")
                title = f"{vote_author.display_name} Judge Election @{vote_author.mention}"
            case VoteTypeEnum.ElectionAdmin:
                author = "Admin Election"
                colour = discord.Colour.from_str("#6600CC")
                title = f"{vote_author.display_name} Admin Election @{vote_author.mention}"
            case VoteTypeEnum.ElectionWardenry:
                author = "Wardenry Election"
                colour = discord.Colour.from_str("#606060")
                title = f"{vote_author.display_name} Wardenry Election @{vote_author.mention}"
            case VoteTypeEnum.ElectionTechnical:
                author = "Technical Election"
                colour = discord.Colour.from_str("#66CC00")
                title = f"{vote_author.display_name} Technical Election @{vote_author.mention}"
            case VoteTypeEnum.Impeachment:
                if member_against is None:
                    print("The member to against is not provided!")
                    return None
                author = "Impeachment"
                colour = discord.Colour.from_str("#FF0000")
                title = f"{zettlekasten_tag} Impeachment {vote_author.display_name} V.s. {member_against.display_name}"
            case VoteTypeEnum.Invite:
                author = "New member vote"
                colour = discord.Colour.from_str("#00FF00")
                title = f"New member vote for {vote_author.display_name}"
        return discord.Embed(
            title = title,
            author = author,
            description = vote_message,
            timestamp = datetime.datetime.now(),
            colour = colour
        )

    @staticmethod
    def generateResult(title: str, agreed: List[discord.Member], against: List[discord.Member], waiver: List[discord.Member], vote_type: VoteTypeEnum) -> discord.Embed:
        decision: str = ""
        if len(agreed) > len(against):
            decision = "Agree"
        elif len(agreed) < len(against):
            decision = "Against"
        elif len(agreed) == len(against):
            decision = "Draw"
        participant_count: int = len(agreed + against + waiver)
        title: str = title
        author: str = vote_type.value
        description: str = f"The Vote has {len(agreed)} agree votes,  {len(against)} against votes, and {len(waiver)} waiver votes. So the decision of this vote is {decision}."
        colour: discord.Colour = UIVoting.determine_colour(vote_type)
        return discord.Embed(
            title = title,
            author = author,
            description = description,
            timestamp = datetime.datetime.now(),
            colour = colour
        )

class UINewUserQuestions(discord.ui.View):
    async def __init__(self, difficulty: UIQuestionDifficultyEnum, user: Union[discord.Member, discord.User]):
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
        self.questions: List[Dict[str, Union[uuid.UUID, str, Dict[str, str], str]]] = await db.get_questions(difficulty)
        question_validaion: List[bool] = []
        # Randomise questions?
        '''Optional
        - [ ] Randomise the question list
        - [ ] Randomise the choices of each question
        '''
        # TODO

        for question in questions:
            _ = discord.ui.Select(
                custom_id = f"{user.id}@{question['UUID']}",
                options = [discord.SelectOption(label=question["Choices"][key], value=key) for key in question["Choices"]],
                placeholder = question["Question"],
                disabled = False
            )
            _.callback = self.cbSelectValidateAnswer
            self.add_item(_)
        
        '''TODO
        - [ ] Add callback to the buttons
        '''
        submit: discord.ui.Button = discord.ui.Button(custom_id=f"{user.id}@question_submit", label="Submit", style=discord.ButtonStyle.success, disabled=True)
        cancel: discord.ui.Button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger, disabled=False)
        submit.callback = self.buttonSubmit
        cancel.callback = self.buttonCancel
        self.add_item(submit)
        self.add_item(cancel)

    def determinePass(self) -> bool:
        correct: int = len([i for i in self.question_validation if i])
        incorrect: int = len([i for i in self.question_validation if not i])

    async def cbSelectValidateAnswewr(self, interaction: discord.Interaction):
        custom_id: str = interaction.data["custom_id"]
        question: dict = None
        for i in self.questions:
            if i["UUID"] == custom_id:
                question = i
                break
        for i in self.children:
            if i.custom_id == custom_id:
                i.disabled = True
                choice: str = i.values[0]
                i.placeholder = f"{'Correct ' if choice == question['Answer'] else 'Incorrect '}" + i.placeholder
                break
        select_options: List[discord.ui.select.Select] = [i for i in self.children if isinstance(i, discord.ui.select.Select) and i.disabled == False]
        if len(select_options) == 0:
            for i in self.children:
                if i.custom_id.split('@')[-1] == "question_submit":
                    i.disabled = False
                    break
        await interaction.response.edit_message(view=self)
        self.question_validation.append(choice == question['Answer'])

    async def buttonSubmit(self, interaction: discord.Interaction):
        if self.determinePass():
            await interaction.response.send_message(content="Congratulations! You pass the test!", ephemeral=True)
        else:
            await interaction.response.send_message(content="You failed!", ephemeral=True)

    async def buttonCancel(self, interaction:discord.Interaction):
        await interaction.response.defer()
        await interaction.delete_original_response()

def dictGetKeystrFromValue(d: Dict[str, Union[int, str]], value: Union[int, str]) -> str:
    return list(d.keys())[list(d.values()).index(value)]

class UIControlPanel(discord.ui.View):
    def __init__(self, member: discord.Member):
        super().__init__()
        role: List[discord.Role] = member.roles
        self.roles: List[str] = [dictGetKeystrFromValue(ROLE_ID_LIST, x) for x in role]
        self.official_roles: List[str] = [x for x in self.roles if x in ROLE_ROLE_LIST["Official"]]
        self.electorate_roles: List[str] = [x for x in self.roles if x in ROLE_ROLE_LIST["Electorate"]]
        self.identity_roles: List[str] = [x for x in self.roles if x in ROLE_ROLE_LIST["Identity"]]
        if "Temp" in identity_roles:
            button1 = discord.ui.Button(label="Take test")
            button1.callback = self.raise_questions
            return

    async def disable_stop(self):
        for item in self.children:
            item.disabled = True
        self.stop()

    async def raise_election(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="", view=UIRaiseVoting(), ephemeral=True)
        await self.disable_stop()

    async def raise_questions(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="", view=(), ephemeral=True)
        await self.disable_stop()

    async def raise_court(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="", view=(), ephemeral=True)
        await self.disable_stop()

    async def raise_appeal(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="", view=(), ephemeral=True)
        await self.disable_stop()
