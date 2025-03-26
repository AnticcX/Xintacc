import time, discord
from discord import User as DiscordUser
from .content import Content
from .response import Response
from ..utils import get_config

# TODO REWRITE THIS SHIT
class User:
    def __init__(self, author: DiscordUser):
        self.author: discord.User = author
        self.queued_messages: Content = Content()
        self.responding_to: Content = Content()
        self.queued_response: str = None
        self.last_requested: float = -1
        self.is_requesting: bool = False
        self.response_message: Response = None
        
        # temp solution
        self.response_channel: discord.TextChannel = None
        
    def add_message(self, message: discord.Message) -> None:
        text = message.content
        self.response_channel = message.channel
        if len(text) > 0:
            self.queued_messages.add_user(text=[message.content])
            
    def clear_queued_messages(self) -> None:
        self.queued_messages = Content(init_list=[msg for msg in self.queued_messages if msg not in self.responding_to])
        
    def can_request(self) -> bool:
        if time.time() - self.last_requested >= get_config("user_request_cooldown"):
            return True
        return False
    
    def finish_request(self) -> None:
        self.queued_response = None
        self.response_message = None
        