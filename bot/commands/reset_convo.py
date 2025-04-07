import discord

from discord.ext import commands
from discord import app_commands

from bot import DiscordClient
from bot import reset_conversation


class resetConvo(commands.Cog):
    def __init__(self, client: DiscordClient):
        self.client = client
    
    @app_commands.command(
        name="reset", 
        description="Resets the user's current conversation"
        )
    async def reset(self, interaction: discord.Interaction):
        reset_conversation(interaction.guild.id, interaction.user.id)
        await interaction.response.send_message(f"{interaction.user.mention} was resetted!")
        
    async def cog_load(self):
        self.client.tree.add_command(self.reset, guild=self.client.MY_GUILD_OBJ)
        
async def setup(client: DiscordClient):
    await client.add_cog(resetConvo(client))
    print(f'Cog {__name__} loaded!')
