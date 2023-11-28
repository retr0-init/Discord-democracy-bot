import discord
import traceback
import os
import asyncio

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
- [x] Automatically give role based on vote result and vote raise
- [x] Replace the technical admin position to propaganda admin
- [ ] Voting for the Guild officer should be one vote per electorate
'''

voting_users: Dict[str, List[int]] = {
    "Left": [],
    "Right": [],
    "Anarchy": [],
    "Extreme": [],
    "Mild": []
}

class UIRaiseElectionElectionAbstract(discord.ui.Modal):

    election_abstract = discord.ui.TextInput(
        label = "你的選舉綱領是？",
        style = discord.TextStyle.long,
        placeholder = "輸入你的選舉綱領...",
        required = True
    )

    def __init__(self, selected_role: str, author: discord.Member):
        electorates: list = [ROLE_ID_LIST[i] for i in ROLE_ROLE_LIST["Electorate"]]
        for i in author.roles:
            if i.id in electorates:
                role_id = i.id
                break
        self.electoral: str = list(ROLE_ID_LIST.keys())[list(ROLE_ID_LIST.values()).index(role_id)]
        title = f"{selected_role}{f' in {self.electoral} electorals' if selected_role == 'Admin' or selected_role == 'Judge' else ''}"
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
        if self.selected_role == "Admin":
            vote_type: VoteTypeEnum = VoteTypeEnum.ElectionAdmin
        elif self.selected_role == "Judge":
            vote_type: VoteTypeEnum = VoteTypeEnum.ElectionJudge
        elif self.selected_role == "Wardenry":
            vote_type: VoteTypeEnum = VoteTypeEnum.ElectionWardenry
        elif self.selected_role == "Propaganda":
            vote_type: VoteTypeEnum = VoteTypeEnum.ElectionPropaganda
        view: discord.View = UIVoting(vote_type=vote_type, author=interaction.user, timeout=604800.0)
        embed = UIVoting.generate_embed(vote_type=vote_type, vote_author=interaction.user, vote_message=self.election_abstract.value)
        view.thread, view.message = await election_channel.create_thread(
            name=f"{interaction.user.display_name} Election as {self.selected_role}",                       # Election vote title
            content=None,                       # Plain text body. Perbably not required.
            embed=embed,                        # Rich text body 
            view=view,                          # voting button view 
            reason=f"Created Election - {self.selected_role}",
            slowmode_delay=1,                   # slow mode delay for 1 second
            applied_tags=[],
            auto_archive_duration=1440          # Auto archived period. Must be 1 hour (60), 1 day (1440), 3 days (4320) or 7 days (10080)
        )
        await interaction.response.send_message(content=f"Thanks for participating the election as {self.selected_role}! Your election proposal has been sent to the election channel.", ephemeral=True)

        await asyncio.sleep(60*60*24*3)
        await view.on_timeout()

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message("好像有什麼出錯了!請確認輸入資訊.", ephemeral=True)
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
            discord.SelectOption(label="行政管理员",     value="Admin"),     # Role Admin
            discord.SelectOption(label="法官",     value="Judge"),     # Role Judge
            discord.SelectOption(label="Propaganda", value="Propaganda"), # Role Propaganda
            discord.SelectOption(label="监狱管理员",  value="Wardenry")   # ardenry
        ],
        placeholder = "選擇你想要選的管理員"
    )
    async def select_role(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        selected_option : str = select_item.values[0]
        self.selected_role_str : str = selected_option
        await interaction.response.send_modal(UIRaiseElectionElectionAbstract(self.selected_role_str, self.author))
        await interaction.delete_original_response()
    



class UIRaiseVoting(discord.ui.Modal, title="Raise a vote"):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Select(
            options = [
                discord.SelectOption(label="一般",        value="Normal"),
                discord.SelectOption(label="公會事務", value="Guild Affairs"),
                discord.SelectOption(label="Constitution",   value="Institution"),
                discord.SelectOption(label="法律",           value="Law")
            ],
            placeholder = "選擇投票的類型"
        ))
        self.add_item(discord.ui.TextInput(
            label = "What is the question of your raised vote?",
            placeholder = "輸入你對投票的問題...",
            required = True
        ))

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"感謝你的投票, {self.name.value}", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message("好像有什麼出錯了!請確認輸入資訊.", ephemeral=True)
        traceback.print_exception(type(error), error, error.__traceback__)

class UIVotingButton(discord.ui.Button):
    def __init__(self, label: str, button_type: UIVotingButtonEnum, custom_id: str, vote_type: VoteTypeEnum, all_lists: Dict[str, List[Union[discord.user, discord.Member]]], row: Optional[int] = None, electorate: Optional[discord.Role] = None):
        self.vote_type: VoteTypeEnum = vote_type
        self.button_type: UIVotingButtonEnum = button_type
        self.users: List[discord.Member] = all_lists[button_type.value]
        self.all_user_lists: Dict[str, List[discord.Member]] = all_lists
        self.electorate: Optional[discord.Role] = electorate
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
        # assert self.view is not None
        view: UIVoting = self.view
        buttons = view.buttons
        vote_type: VoteTypeEnum = view.vote_type
        user: Union[discord.User, discord.Member] = interaction.user
        list_bool: List[bool] = [user in x for x in self.all_user_lists.values()]
        electorate_str: str = list(ROLE_ID_LIST.keys())[list(ROLE_ID_LIST.values()).index(self.electorate.id)]
        vote_invalid: bool = False
        message_to_send: str = ""
        message_valid: str = ""
        message_type: str = ""
        duplicate: bool = False
        await self.customCallback(interaction)
        if user.id in voting_users[electorate_str]:
            print("You have voted for one of the nominators of this electorate.")
            vote_invalid = True
            message_valid = "You have voted for one of the nominators of this electorate."
            # await interaction.response.send_message(content="You have voted for one of the nominators of this electorate.", ephemeral=True)
        else:
            voting_users[electorate_str].append(user.id)
        print(vote_type, user, list_bool, self.all_user_lists)
        if not any(list_bool):
            match vote_type:
                case VoteTypeEnum.ElectionJudge:
                    if self.electorate in user.roles:
                        if not vote_invalid:
                            self.users.append(user)
                        message_type = f"你投的票是{self.button_type.name}"
                        # await interaction.response.send_message(content=f"你投的票是{self.button_type.name}", ephemeral=True)
                    else:
                        message_type = f"You do not belong to this electorate."
                        # await interaction.response.send_message(content=f"You do not belong to this electorate.", ephemeral=True)
                case _:
                    if not vote_invalid:
                        self.users.append(user)
                    message_type = f"你投的票是{self.button_type.name}"
                    # await interaction.response.send_message(content=f"你投的票是{self.button_type.name}", ephemeral=True)
        else:
            duplicate = True
            message_type = f"你已經投過{list(self.all_user_lists.keys())[list_bool.index(True)]}!"
            # await interaction.response.send_message(content=f"你已經投過{list(self.all_user_lists.keys())[list_bool.index(True)]}!", ephemeral=True)
        if not vote_invalid or duplicate:
            message_to_send = message_type
        else:
            message_to_send = message_valid
        await interaction.response.send_message(content=message_to_send, ephemeral=True)
        # TODO check user permission with the database check

    async def customCallback(self, interaction: discord.Interaction):
        pass

class UIVoting(discord.ui.View):
    
    id: uuid.UUID = None
    created: datetime.datetime = None
    expired: datetime.datetime = None
    finished: bool = False
    vote_type: VoteTypeEnum = None
    voter_limited: bool = False
    voters: Optional[List[Union[discord.User, discord.Member]]] = []
    agree: List[Union[discord.User, discord.Member]] = []
    against: List[Union[discord.User, discord.Member]] = []
    waiver: List[Union[discord.User, discord.Member]] = []
    jump_url: str = ""
    buttons: List[UIVotingButton] = []
    clicked_users: List[int] = []

    colour: List[Optional[discord.Colour]] = [None]
    # https://stackoverflow.com/questions/69265909/discord-py-edit-the-interaction-message-after-a-timeout-in-discord-ui-select
    message: Optional[discord.Message] = None
    thread: Optional[discord.Thread] = None


    def __init__(self, vote_type: VoteTypeEnum, author: discord.Member, timeout: float = 100.0):
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
        self.author_electorate: discord.Role = [j for j in [author.guild.get_role(ROLE_ID_LIST[i]) for i in ROLE_ROLE_LIST["Electorate"]] if j in self.author.roles][0]

        for vote_option in UIVotingButtonEnum:
            label = vote_option.value
            button = UIVotingButton(label=label, button_type=vote_option, custom_id=None, all_lists=self.vote_dict, vote_type=vote_type, row=2, electorate=self.author_electorate)
            self.buttons.append(button)
            self.add_item(button)

    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)
        self.stop()

    def determine_vote_pass(self) -> bool:
        return len(self.agree) - len(self.against) >= 30

    async def on_timeout(self):
        print("TIMEOUT TIMEOUT")
        await self.message.channel.send(f"超出時間.投票的結果{'已通過' if self.determine_vote_pass() else '還沒通過'}. 此串將會被記錄跟鎖定.")
        await self.disable_all_items()
        await self.thread.edit(archived=True, locked=True, reason="The Vote completes. The thread is archived and locked.")
        name: str = ""
        content: str = ""
        embed: discord.Embed = discord.Embed()
        reason: str = ""
        influence_ratio = len(self.agree + self.against + self.waiver) / self.thread.guild.member_count
        match self.vote_type:
            case VoteTypeEnum.ElectionJudge:
                if self.determine_vote_pass():
                    given_role: discord.Role = self.message.guild.get_role(ROLE_ID_LIST["Judge"])
                    await self.author.add_roles(given_role, reason = "Election completed. Judge role added to {}.".format(self.author.display_name))
                name: str = f"{self.author.display_name} is {'' if self.determine_vote_pass() else 'NOT '}elected as Judge in {list(ROLE_ID_LIST.keys())[list(ROLE_ID_LIST.values()).index(self.author_electorate.id)]} electorate"
                content: str = f"投票率：{influence_ratio}\nJudge Election completes. The result is:"
                embed: discord.Embed = discord.Embed(
                    description = f"# 結果: {self.author.mention} {'沒有被 ' if not self.determine_vote_pass() else ''}選為法官.\n## 同意: {len(self.agree)}\n## 不同意: {len(self.against)}\n## 棄票: {len(self.waiver)}",
                    timestamp = datetime.datetime.now()
                )
                reason = "Election Judge result is published."
            case VoteTypeEnum.ElectionAdmin:
                if self.determine_vote_pass():
                    given_role: discord.Role = self.message.guild.get_role(ROLE_ID_LIST["Admin"])
                    await self.author.add_roles(given_role, reason = "Election completed. Admin role added to {}.".format(self.author.display_name))
                name: str = f"{self.author.display_name} is elected as Admin."
                content: str = f"投票率：{influence_ratio}\nAdmin Election completes. The result is:"
                embed: discord.Embed = discord.Embed(
                    description = f"# 結果: {self.author.mention} {'沒有被 ' if not self.determine_vote_pass() else ''}選為行政管理員.\n## 同意: {len(self.agree)}\n## 不同意: {len(self.against)}\n## 棄票: {len(self.waiver)}",
                    timestamp = datetime.datetime.now()
                )
                reason = "Election Admin result is published."
            case VoteTypeEnum.ElectionWardenry:
                if self.determine_vote_pass():
                    given_role: discord.Role = self.message.guild.get_role(ROLE_ID_LIST["Wardenry"])
                    await self.author.add_roles(given_role, reason = "Election completed. Wardenry role added to {}.".format(self.author.display_name))
                name: str = f"{self.author.display_name} is elected as Wardenry."
                content: str = f"投票率：{influence_ratio}\nWardenry Election completes. The result is:"
                embed: discord.Embed = discord.Embed(
                    description = f"# 結果: {self.author.mention} {'沒有被 ' if not self.determine_vote_pass() else ''}選為監獄管理員.\n## 同意: {len(self.agree)}\n## 不同意: {len(self.against)}\n## 棄票: {len(self.waiver)}",
                    timestamp = datetime.datetime.now()
                )
                reason = "Election Wardenry result is published."
            case VoteTypeEnum.ElectionPropaganda:
                if self.determine_vote_pass():
                    given_role: discord.Role = self.message.guild.get_role(ROLE_ID_LIST["Propaganda"])
                    await self.author.add_roles(given_role, reason = "Election completed. Propaganda role added to {}.".format(self.author.display_name))
                name: str = f"{self.author.display_name} is elected as Propaganda."
                content: str = f"投票率：{influence_ratio}\nPropaganda Election completes. The result is:"
                embed: discord.Embed = discord.Embed(
                    description = f"# 結果: @{self.author.mention} {'沒有被 ' if not self.determine_vote_pass() else ''}選為技術管理員.\n## 同意: {len(self.agree)}\n## 不同意: {len(self.against)}\n## 棄票: {len(self.waiver)}",
                    timestamp = datetime.datetime.now()
                )
                reason = "Election Propaganda result is published."
        channelPublish: discord.Channel = await self.message.guild.fetch_channel(CHANNEL_ID_LIST["Publish"])
        await channelPublish.create_thread(
            name = name,
            content = content,
            embed = embed,
            reason = reason,
            applied_tags = [],
            #file = discord.File()
        )
        self.agree.clear()
        self.against.clear()
        self.waiver.clear()
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
            case VoteTypeEnum.ElectionPropaganda:
                colour = discord.Colour.from_str("#66CC00")
            case VoteTypeEnum.Impeachment:
                colour = discord.Colour.from_str("#FF0000")
            case VoteTypeEnum.Invite:
                colour = discord.Colour.from_str("#00FF00")
            case _:
                colour = discord.Colour.dark_grey

        return colour

    @staticmethod
    def generate_embed(vote_type: VoteTypeEnum, vote_author: discord.Member, vote_message: str, member_against: Optional[discord.Member] = None) -> Optional[discord.Embed]:
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
                title = f"{vote_author.display_name} Judge Election {vote_author.mention}"
            case VoteTypeEnum.ElectionAdmin:
                author = "Admin Election"
                colour = discord.Colour.from_str("#6600CC")
                title = f"{vote_author.display_name} Admin Election {vote_author.mention}"
            case VoteTypeEnum.ElectionWardenry:
                author = "Wardenry Election"
                colour = discord.Colour.from_str("#606060")
                title = f"{vote_author.display_name} Wardenry Election {vote_author.mention}"
            case VoteTypeEnum.ElectionPropaganda:
                author = "Propaganda Election"
                colour = discord.Colour.from_str("#66CC00")
                title = f"{vote_author.display_name} Propaganda Election {vote_author.mention}"
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
            #author = author,
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
        submit: discord.ui.Button = discord.ui.Button(custom_id=f"{user.id}@question_submit", label="發送", style=discord.ButtonStyle.success, disabled=True)
        cancel: discord.ui.Button = discord.ui.Button(label="取消", style=discord.ButtonStyle.danger, disabled=False)
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
            await interaction.response.send_message(content="恭喜你通過了測驗!", ephemeral=True)
        else:
            await interaction.response.send_message(content="你沒通過!", ephemeral=True)

    async def buttonCancel(self, interaction:discord.Interaction):
        await interaction.response.defer()
        await interaction.delete_original_response()

class UISelectLaw(discord.ui.Select):
    def __init__(self, message: discord.Message, laws: List[str]):
        super().__init__()
        self.message_reported = message
        for law in laws:
            self.add_option(label=law)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(UIModalCourtDetails(self.message_reported, self.values[0], discord.Embed()))
        await interaction.delete_original_response()

class UIViewCourt(discord.ui.View):
    def __init__(self, court_stage: CaseStepEnum):
        super().__init__()
        self.agree: List[discord.Member] = []
        self.against : List[discord.Member] = []
        user_list: dict = {"Agree": self.agree, "Against": self.against}
        match court_stage:
            case CaseStepEnum.First:
                pass
            case CaseStepEnum.Second:
                self.add_item(UIVotingButton("Agree", UIVotingButtonEnum.Agree, None, VoteTypeEnum.Justice, user_list, row = 2))
                self.add_item(UIVotingButton("Against", UIVotingButtonEnum.Against, None, VoteTypeEnum.Justice, user_list, row = 2))
                pass

    async def close_case(self, interaction: discord.Interaction):
        for item in self.children:
            item.disabled = True
        await interaction.channel.starter_message.edit(view=self)
        await interaction.response.send_message("This case is closed.")
        interaction.channel.locked = True
        self.stop()

class UIModalCourtDetails(discord.ui.Modal):
    details: discord.ui.TextInput = discord.ui.TextInput(
        label = "Please enter the details of this appeal. The message you want to report will appear in the court as the evidence.",
        style = discord.TextStyle.long,
        required = True,
        placeholder = "Please enter the details of this appeal..."
    )

    def __init__(self, message: discord.Message, law: str, law_embed: discord.Embed):
        super().__init__()
        self.message_reported: discord.Message = message
        self.law: str = law
        self.law_embed: discord.Embed = law_embed

    async def on_submit(self, interaction):
        channel = await interaction.guild.fetch_channel(CHANNEL_ID_LIST["Court"])
        await channel.create_thread(
            name = f"{interaction.user.display_name} V.s. {self.message_reported.author.display_name} {datetime.datetime.now(datetime.timezone.utc).strftime('UTC%Y%m%d%H%M%S')}",
            content = f'''Time (UTC): {datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")}
            Appealor: {interaction.user.mention}
            Appealee: {self.message_reported.author.mention}
            Law Offense: {self.law}
            Message reported: 
            - Link: {self.message_reported.jump_url}
            - Author: {self.message_reported.author.mention}
            - Content: {self.message_reported.content}
            Details: {self.details.value}

            All judges please attend and host this court. {interaction.guild.get_role(ROLE_ID_LIST["Judge"]).mention}
            ''',
            embed = self.law_embed,
            view = UIViewCourt(CaseStepEnum.First),
            auto_archive_duration = 1440,   # Archive this post after 24 hours
            reason = f"Court {interaction.user.id} V.S. {self.message_reported.author.id} on message {self.message_reported.jump_url} whose content is [{self.message_reported.content}]."
        )
        await interaction.response.send_message(content="The court thread has already been created!", ephemeral=True)

def dictGetKeystrFromRoleValue(d: Dict[str, Union[int, str]], value: Union[int, str]) -> str:
    return list(d.keys())[list(d.values()).index(value.id)]

class UIControlPanel(discord.ui.View):
    def __init__(self, member: discord.Member, channel: Union[discord.abc.GuildChannel, discord.Thread]):
        super().__init__()
        role: List[discord.Role] = member.roles
        self.roles: List[str] = []#[dictGetKeystrFromRoleValue(ROLE_ID_LIST, x) for x in role if x.name != "@everyone"]
        for x in role:
            if x.name != "@everyone":
                try:
                    self.roles.append(dictGetKeystrFromRoleValue(ROLE_ID_LIST, x))
                except:
                    pass
        self.official_roles: List[str] = [x for x in self.roles if x in ROLE_ROLE_LIST["Official"]]
        self.electorate_roles: List[str] = [x for x in self.roles if x in ROLE_ROLE_LIST["Electorate"]]
        self.identity_roles: List[str] = [x for x in self.roles if x in ROLE_ROLE_LIST["Identity"]]
        if "Temp" in self.identity_roles:
            button1 = discord.ui.Button(label="做個測驗")
            button1.callback = self.raise_questions
            #self.add_item(button1)
        elif "Prisoner" in self.identity_roles:
            button1 = discord.ui.Button(label="上交申訴書")
            button1.callback = self.raise_appeal
            #self.add_item(button1)
        elif "Judge" in self.identity_roles and isinstance(channel, discord.Thread) and not isinstance(channel.parent, None):
            if channel.parent.id == CHANNEL_ID_LIST["Court"]:
                button1 = discord.ui.Button(label="Close Court")
                button.callback = self.close_court
                #self.add_item(button1)
        else:
            button1 = discord.ui.Button(label="選舉")
            button1.callback = self.raise_election
            button2 = discord.ui.Button(label="法庭")
            button2.callback = self.raise_court
            self.add_item(button1)
            # self.add_item(button2)

    async def disable_stop(self):
        for item in self.children:
            item.disabled = True
        self.stop()

    async def raise_election(self, interaction: discord.Interaction):
        if len([i for i in [ROLE_ID_LIST[j] for j in ROLE_ROLE_LIST["Electorate"]] if interaction.guild.get_role(i) in interaction.user.roles]) == 0:
            await interaction.response.edit_message(content="請您先選擇選區", view=None)
        elif len([i for i in [ROLE_ID_LIST[j] for j in ROLE_ROLE_LIST["Official"]] if interaction.guild.get_role(i) in interaction.user.roles]) == 0:
            await interaction.response.edit_message(content="選擇你要選的職位", view=UIRaiseElection(interaction.user))
        else:
            await interaction.response.edit_message(content="您已經是管理，不能參與選舉", view=None)
        await self.disable_stop()

    async def raise_questions(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="", view=())
        await self.disable_stop()

    async def raise_court(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="請選擇你要申訴的人然後輸入細節", view=())
        await self.disable_stop()

    async def close_court(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="The court is closed", eohemeral=True)

    async def raise_appeal(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="請選擇你要申訴的案件", view=(), ephemeral=True)
        await self.disable_stop()

    async def raise_impeachment(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="", view=())
        await self.disable_stop()
