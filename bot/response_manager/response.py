from discord import Message, Embed, Attachment
from datetime import datetime

from ..utils import get_config

#TODO tf is this even used for? maybe image generation?
class Response:
    def __init__(self, message: Message, embed: Embed = None):
        self.message: Message = message
        self.embed: Embed = embed
    
    async def edit_embed(self, embed: Embed, attachments: list[Attachment] = []) -> None:
        await self.message.edit(embed=embed, attachments=attachments)
        