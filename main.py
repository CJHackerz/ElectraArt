import discord
from discord.ext import commands
import logging
import os
from InteractionProc.BotApiActions import UserApi, UpvoteApi

bot_token = os.getenv('DISCORD_BOT_TOKEN')
logging.basicConfig(encoding='utf-8', level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

class ElectraArt(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="/",
        intents = discord.Intents(message_content=True, guilds=True, guild_messages=True, members=True, guild_reactions=True, guild_typing=True, dm_messages=False, dm_reactions=False),
        application_id = 1072739308999553194)
    
    async def setup_hook(self) -> None:
        await self.load_extension(f"cogs.baseline")
        await bot.tree.sync()

    async def on_ready(self):
        logging.info("=== ElectraArt bot is operational! ===")

bot = ElectraArt()
bot.run(bot_token)