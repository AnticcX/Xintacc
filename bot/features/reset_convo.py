import discord

from discord.ext import commands
from discord import app_commands

from ..response_manager import reset_conversation
from bot import discordClient


class resetConvo(commands.Cog):
    def __init__(self, client: discordClient):
        self.client = client
    
    @app_commands.command(
        name="reset", 
        description="Resets the user's current conversation"
        )
    async def reset(self, interaction: discord.Interaction):
        reset_conversation(str(interaction.user.id))
        await interaction.response.send_message(f"{interaction.user.mention} was resetted!")
        
    async def cog_load(self):
        # Attach command directly to the tree
        self.client.tree.add_command(self.reset, guild=self.client.MY_GUILD_OBJ)
        print("✅ Slash command added to tree")
        
async def setup(client: discordClient):
    await client.add_cog(resetConvo(client))
    print(f'Cog {__name__} loaded!')
