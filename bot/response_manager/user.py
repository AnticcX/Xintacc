import time, discord

from discord import User as DiscordUser

from .content import Content
from .response import Response
from bot import get_config
from bot import DiscordMessage

# TODO REWRITE THIS SHIT
class User:
    def __init__(self, guild_id: int, author: DiscordUser):
        self.author: discord.User = author
        self.queued_messages: MessageQueue = MessageQueue()
        self.responding_to: Content = Content()
        self.queued_response: str = None
        self.last_requested: float = -1
        self.is_requesting: bool = False
        self.response_message: Response = None
        self.guild_id: int = guild_id
        
        # temp solution
        self.response_channel: discord.TextChannel = None
        
    async def add_message(self, message: DiscordMessage) -> None:
        if not self.queued_messages.image_thread:
            self.queued_messages.image_thread = message.channel.get_thread(get_config("image_thread_id"))
        
        self.response_channel = message.channel
            
        text = message.content
        await self.queued_messages.add(text=text)
        
        if not message.original_message:
            return
        
        for attachment in message.original_message.attachments:
            if attachment.content_type and attachment.content_type.startswith('image/'):
                await self.queued_messages.add(image=attachment)
        
    def generate_response_queue(self) -> None:
        self.responding_to.add_user(texts=self.queued_messages.texts, image_urls=self.queued_messages.images)
        
    def can_request(self) -> bool:
        if time.time() - self.last_requested >= get_config("user_request_cooldown"):
            return True
        return False
    
    def finish_request(self) -> None:
        self.queued_response = None
        self.response_message = None
        self.responding_to = Content()
        
        
class MessageQueue:
    def __init__(self):
        self.texts: list = []
        self.images: list = []
        self.image_thread: discord.Thread = None
        
    async def upload_image(self, image: discord.File) -> str:
        image_msg = await self.image_thread.send(file=image)
        return image_msg.attachments[0].url
        
    async def add(self, text: str = None, image: discord.Attachment = None) -> None:
        if text:
            self.texts.append(text)
        if image:
            image_url = await self.upload_image(image.to_file())
            self.images.append(image_url)
            
    def clear(self):
        self.texts = []
        self.images = []
        
    def __len__(self):
        return len(self.texts) + len(self.images)
    
    def __iter__(self):
        iterable = self.texts + self.images
        return iter(iterable)
    
    def __call__(self):
        return self.texts + self.images