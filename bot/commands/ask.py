from discord.ext import commands
from discord import app_commands, Interaction, Object

from bot import DiscordClient, DiscordMessage

MY_GUILD = Object(id=764920345282084865)

class askBot(commands.Cog):
    def __init__(self, client: DiscordClient):
        self.client = client
    
    @app_commands.command(
        name="ask", 
        description="Ask Xintacc a question and he will answer.",
        )
    @app_commands.describe(prompt="What would you like to ask?")
    async def ask(self, interaction: Interaction, prompt: str):
        message = DiscordMessage(
            channel=interaction.channel,
            author=interaction.user,
            content=prompt
        )
        
        await self.client.queue_message(message)
        await interaction.response.send_message("Xintacc has queued your prompt!", ephemeral=True)
            
    
    async def cog_load(self):
        self.client.tree.add_command(self.ask, guild=MY_GUILD)
    
async def setup(client: DiscordClient):
    await client.add_cog(askBot(client))
    print(f'Cog {__name__} loaded!')