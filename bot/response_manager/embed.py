import time

from discord import Embed, Color
from datetime import datetime

from .user import User
from ..utils import get_config
from .content import Content

#TODO REWRITE CLEANER CODE
class Embed(Embed):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args, 
            **kwargs,
            )
    
    @staticmethod
    def formatted_queue(queue: Content) -> str:
        """
        Formats the message queue into a string, limiting message length
        and preserving Discord CDN image links.

        Args:
            queue (Content): The user's queued message content.

        Returns:
            str: A newline-separated string of text and image URLs.
        """
        field_char_limit = get_config("field_character_limit")

        def format_entry(entry: dict) -> str:
            if "text" in entry:
                text: str = entry["text"]
                if len(text) > field_char_limit and not text.startswith("https://cdn.discordapp.com/attachments/"):
                    return text[:field_char_limit]
                return text
            elif "image_url" in entry:
                return entry["image_url"]["url"]
            return ""

        return "\n".join(
            format_entry(element)
            for content_block in queue
            for element in content_block.get("content", [])
        )
        
    def complete(self, user: User) -> None:
        self.set_color(get_config("successful_color"))
        self.title = "Xintacc responded with:"
        self.description = user.queued_response[:4000]
        footer_text = f"Response took {round(time.time() - user.last_requested, 2)} seconds."
        
        if self.description != user.queued_response:
            self.set_color(get_config("incomplete_color"))
            self.title = "Xintacc responded with **(incomplete response)**:"
            footer_text += " | View attached file for complete response"
            
            
            
        self.set_footer(text=footer_text)
        
        if len(self.fields) > 1:
            self.remove_field(1)
        
        self.set_field_at(index=0, name="Responded to:", value=self.fields[0].value, inline=False)
        
    def start_response(self, user: User) -> None:
        self.set_color(get_config("pending_color"))
        self.set_author(name=f"{user.author.display_name}", icon_url=user.author.avatar.url)
        if len(self.fields) <= 2:
            self.remove_field(1)
        self.insert_field_at(index=0, name="Responding to:", value=self.formatted_queue(user.responding_to), inline=True)
            
    def pending_response(self, user: User, on_cooldown: bool = False) -> None:
        queued_messages = self.formatted_queue(user.queued_messages)
        request_cooldown = get_config("user_request_cooldown")
        cooldown_elapsed_time = int(time.time() - user.last_requested)
        can_edit_footer = (not bool(self.footer) or self.footer.text != f"You are in cooldown for {request_cooldown - cooldown_elapsed_time} seconds..")
        self.set_color(get_config("failed_color") if not on_cooldown and not user.is_requesting else get_config("pending_color"))
        
        if len(self.fields) <= 2 or self.fields[1].value != queued_messages:
            try:
                self.set_field_at(index=1, name="Prompts Queued:", value=queued_messages, inline=False)
            except IndexError:
                self.insert_field_at(index=1, name="Prompts Queued:", value=queued_messages, inline=False)
            
            if on_cooldown and can_edit_footer and not user.is_requesting:
                if len(self.fields) <= 2:
                    self.remove_field(0)
                self.set_footer(text=f"You are in cooldown for {request_cooldown - cooldown_elapsed_time} seconds..")
                
    def set_color(self, rgb: tuple | list = ()) -> None:
        self.color = Color.from_rgb(*rgb)
        