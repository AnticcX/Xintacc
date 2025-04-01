import os, time, io

from discord.ext import commands, tasks
from discord import Message, Intents, File, Object
from threading import Thread

from bot import get_config
from bot import User, Model, Embed, Response

class discordClient(commands.Bot):
    MY_GUILD_ID = Object(id=764920345282084865)
    MODEL_BASE_URL = get_config("model_base_url")
    MODEL = get_config("model")
    MODEL_API_KEY = os.getenv("MODEL_API_KEY")
    RESPONSE_CLIENT = Model(MODEL_BASE_URL, MODEL, MODEL_API_KEY)
    
    def __init__(self, intents) -> None:
        super().__init__(
            command_prefix=get_config("discord_bot_command_prefix"),
            intents=intents,
            help_command=None
        )
        
        self.queued_users: dict[int, User] = {}
        
    async def setup_hook(self):
        await self.load_extensions()
        
        print("🔎 Commands before sync:")
        for cmd in self.tree.get_commands(guild=self.MY_GUILD_ID):
            print(f" - {cmd.name}")
            
        await self.tree.sync(guild=self.MY_GUILD_ID)
        
    async def load_extensions(self):
        for filename in os.listdir("./bot/features"):
            if filename.endswith(".py"):
                await self.load_extension(f"bot.features.{filename[:-3]}")
        
    async def on_ready(self):
        self.process_queued_users.start()
        print(f'Logged in as {self.user} (ID: {self.user.id})') 
        print('------')
        
    async def on_message(self, message: Message):
        if message.author.id == self.user.id or message.author.bot:
            return
        
        if message.content.startswith(get_config("discord_bot_command_prefix")):
            return await self.process_commands(message)
        
        guild_id = None if not message.guild else message.guild.id
        channel_id = message.channel.id
        
        if guild_id not in get_config("allowed_guild_ids") or channel_id not in get_config("allowed_channel_ids"):
            return
        try: 
            user = self.queued_users[message.author.id]
        except KeyError:
            user = self.queued_users[message.author.id] = User(message.author)
                    
        await user.add_message(message)
        await message.delete()
        
    def get_response(self, user: User) -> None:
        user.is_requesting = True
        try:
            user.generate_response_queue()
            user.queued_messages.clear()
            user.last_requested = time.time()
            res = self.RESPONSE_CLIENT.fetch_response(str(user.author.id), user.responding_to)
            user.queued_response = res if res else "Failed to get a response.."
        finally:
            user.is_requesting = False
            
    @tasks.loop(seconds=1.25)
    async def process_queued_users(self):
        for user_id, user in self.queued_users.copy().items():
            emb = Embed()
            if user.response_message and len(user.response_message.message.embeds):
                emb = user.response_message.embed
                
            if user.queued_response:
                emb.complete(user)
                attached_file = None
                
                if emb.description != user.queued_response and get_config("send_large_texts_as_files"):
                    attached_file = File(fp=io.StringIO(user.queued_response), filename=f"output.txt")
                
                await user.response_message.edit_embed(embed=emb, attachments=[attached_file] if attached_file else [])
                user.finish_request()
            elif len(user.queued_messages) > 0 and not user.is_requesting and user.can_request():
                thread = Thread(target=self.get_response, args=[user])
                thread.start()
                emb.start_response(user)
                if not user.response_message:
                    user.response_message = Response(await user.response_channel.send(embed=emb), emb)
                else:
                    await user.response_message.edit_embed(embed=emb)
            elif emb and user.can_request() and user.response_message:
                if len(user.queued_messages) != 0:
                    emb.pending_response(user)
                    await user.response_message.edit_embed(embed=emb)
                    
                cooldown_elapsed_time = int(time.time() - user.last_requested)
                if cooldown_elapsed_time >= 6:
                    emb.set_footer(text=f"This is taking longer than expected.. Please be patient!")
                    await user.response_message.edit_embed(embed=emb)
            elif not user.can_request() and len(user.queued_messages) > 0:
                emb.pending_response(user, on_cooldown=True)
                if not user.response_message:
                    user.response_message = Response(await user.response_channel.send(embed=emb), emb)
                else:
                    await user.response_message.edit_embed(embed=emb)