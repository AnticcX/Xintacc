from discord import User, Member, Message, Embed, File
from discord.abc import Messageable
from typing import Union, Optional


class DiscordMessage:
    """
    A wrapper around a discord.Message or a custom message-like object
    with content, author, and channel.
    """
    def __init__(
        self,
        *,
        message: Optional[Message] = None,
        channel: Optional[Messageable] = None,
        author: Optional[Union[User, Member]] = None,
        content: Optional[str] = None
    ):
        
        self.original_message: Message = None
        
        if message:
            self.content = message.content
            self.author = message.author
            self.channel = message.channel
            self.original_message = message
        else:
            if content is None or author is None or channel is None:
                raise ValueError("When 'message' is not provided, 'content', 'author', and 'channel' must be set.")
            
            self.content = content
            self.author = author
            self.channel = channel

    async def reply(
        self,
        *,
        content: Optional[str] = None,
        embed: Optional[Embed] = None,
        files: Optional[list[File]] = None
        ):
        if not content and not embed and not files:
            raise ValueError("One param must be not None (content, embed, or files)")
        
        if self.original_message:
            await self.original_message.reply(content=content, embed=embed, files=files)
        else:
            await self.channel.send(content=content, embed=embed, files=files)