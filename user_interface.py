import discord
import traceback

'''TODO
- [ ] Create the UI for election, court, normal voting, and moderation
- [ ] UIElection needs to have choice filter based on previous selection
'''


class UIElection(discord.ui.Modal, title="Election"):
    election_role = discord.ui.Select()
    #TODO Will the electable roles all be created individually?
    # election_role = discord.ui.RoleSelect()
    election_channel = discord.ui.ChannelSelect()
    election_abstract = discord.ui.TextInput(
        label = "What is your election abstract?",
        style = discord.TextStyle.long,
        placeholder = "Enter your election abstract here...",
        required = True
    )

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

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Thanks for participating election, {self.name.value}!", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message("Oops! Something went wrong. Please check the information enterred.", ephemeral=True)
        traceback.print_exception(type(error), error, error.__traceback__)


class UIVoting():
    pass
