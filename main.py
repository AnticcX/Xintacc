import os

from discord import Intents
from dotenv import load_dotenv

from bot import DiscordClient

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


if __name__ == "__main__":

    intents = Intents.all()
    intents.message_content = True
    
    client = DiscordClient(intents=intents)
    client.run(token=TOKEN)
