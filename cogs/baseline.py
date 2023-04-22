import discord
from discord import app_commands
from discord.ext import commands
import discord.utils
import sys
import os
import logging
import json
import asyncio
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from InteractionProc.BotApiActions import UserApi, ArtApi, RelationApi, ChatGPTApi, ScoreboardApi, UpvoteApi

class ImageFrame_Btn(discord.ui.View):
    
    @discord.ui.button(emoji="👍🏼", label="Upvote", style=discord.ButtonStyle.primary, custom_id="upvote-btn")
    async def upvote_button(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.defer()
        await UserApi.check_and_add_member(discoMember=interaction.user)
        upvote_status = await UpvoteApi.add_new_upvote(discoMember=interaction.user, discoMessage=interaction.message)
        if upvote_status == "Success":
            await interaction.followup.send(embed=discord.Embed(description="✍🏼 Your feedback has been noted! 👍🏼🗒", color=discord.Color.dark_red()), ephemeral=True)
        else:
            await interaction.followup.send(embed=discord.Embed(description="⚠️ You have already upvoted this art! 🛑🗒", color=discord.Color.dark_red()), ephemeral=True)
    
    @discord.ui.button(emoji="🌠", label="Favorite", style=discord.ButtonStyle.green, custom_id="favourite-btn")
    async def star_button(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != interaction.message.interaction.user.id:
            await interaction.response.defer()
            await UserApi.check_and_add_member(discoMember=interaction.user)
            await interaction.followup.send(embed=discord.Embed(description="✍🏼 Your feedback has been noted! ⭐🗒", color=discord.Color.dark_red()), ephemeral=True)

    @discord.ui.button(emoji="⏬", label="Download", style=discord.ButtonStyle.secondary, custom_id="download-btn")
    async def download_button(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id == interaction.message.interaction.user.id:
            await interaction.response.defer()
            art_url_data = await ArtApi.get_art_url(discoMessage=interaction.message)
            await interaction.followup.send(embed=discord.Embed(title="🤖 Generating download link... ⏬🗒", description="{}".format(art_url_data), color=discord.Color.dark_red()).set_thumbnail(url=art_url_data), ephemeral=True)

        await interaction.response.send_message(embed=discord.Embed(description="⚠️ You can only get download link for the art created by your prompt! 🛑🗒", color=discord.Color.dark_red()), ephemeral=True)
        await UserApi.check_and_add_member(discoMember=interaction.user)

class Baseline(commands.Cog):
    
    iVar_LOCAL_PATH = os.getcwd()
    WHITE_LIST_CONFIG_FILE = open(iVar_LOCAL_PATH + "/allowed_guild.json")
    ALLOWED_LIST = json.load(WHITE_LIST_CONFIG_FILE)
    WHITE_LISTED_SERVERS = ALLOWED_LIST["allowList"]
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    def __del__(self) -> None:
        self.ALLOWED_LIST.close()
    
### Code for /genimage command ###
    @app_commands.command(name="genimage", description="Provides one image based on user given text prompt")
    @app_commands.describe(user_input="Required text prompt to get image from AI")
    async def genimage(self, interaction: discord.Interaction, user_input: str):
    # Log command user to database
        await UserApi.check_and_add_member(discoMember=interaction.user)
    # Update user profile with recent art source
        await UserApi.update_recent_art_src(discoMember=interaction.user)
        if str(interaction.guild_id) in self.WHITE_LISTED_SERVERS:
            await interaction.response.defer()
            image_url = await asyncio.gather(
                asyncio.to_thread(ArtApi.openai_gen_img, user_input)
            )
            image_keywords = await asyncio.gather(
                asyncio.to_thread(ChatGPTApi.executor, "assign_keyword", user_input)
            )
            if image_url[0] != "Error":
                #Setup command output embed frame
                image_embed_head = discord.Embed(title=":frame_photo: " + user_input + " :frame_photo:", color=discord.Color.from_str("#0b67e1"))
                image_embed = discord.Embed(title=":label: Picture Tags:", description=image_keywords[0], color=discord.Color.gold())
                image_embed.set_image(url=image_url[0])
                image_embed.set_footer(text="Property of {}".format(interaction.guild.name))
                # Image button UI
                image_btn = ImageFrame_Btn(timeout=None)
                await interaction.followup.send(embeds=[image_embed_head, image_embed], view=image_btn)
                image_frame = await interaction.original_response()
                #Perform DB operations
                await ArtApi.add_new_art(discoMember=interaction.user, discoMessage=image_frame, ArtTitle=user_input, ArtCDNUrl=image_url[0])
                await RelationApi.join_usr_art(discoMember=interaction.user, discoMessage=image_frame)
                await image_btn.wait()
            logging.info('=== UserInput: {}, ImageURL: {} ==='.format(user_input, image_url[0]))
            
        elif len(user_input) > 254:
            text_embed = discord.Embed(title=":warning: :red_circle: Im Sorry Dave, Im Afraid I Can't Do That :red_circle: :warning:", description="Please give valid prompt under 255 characters, instead of providing any :wastebasket: garbage!", color=discord.Color.red())
            logging.warning("=== Invalid Text Prompt Rejected ===")
            text_embed.set_footer(text="Property of {}".format(interaction.guild.name))
            await interaction.followup.send(embed=text_embed)
        else:
            text_embed = discord.Embed(title=":warning: :red_circle: Im Sorry Dave, Im Afraid I Can't Do That :red_circle: :warning:", description="Code for a programming language and NSFW content is not allowed :no_entry_sign: on :robot: OpenAI DALL-E Servers, stick to professional english text based prompts!", color=discord.Color.red())
            logging.warning("=== Invalid Text Prompt Rejected ===")
            text_embed.set_footer(text="Property of {}".format(interaction.guild.name))
            await interaction.followup.send(embed=text_embed)

### Code for /gentext command ###
    @app_commands.command(name="gentext", description="Answers yours interesting questions with text")
    @app_commands.describe(user_input="Required text prompt to get information from AI")
    async def gentext(self, interaction: discord.Interaction, user_input: str):
        if str(interaction.guild_id) in ["508869814861955072", "368404805716279303", "925467947038830643", "218155098004652042"]:
            await interaction.response.defer()
            # Log command user to database
            await UserApi.check_and_add_member(discoMember=interaction.user)
            text_output = await asyncio.gather(
                asyncio.to_thread(ChatGPTApi.executor, "chatgpt", user_input)
            )
            await interaction.followup.send(embed=discord.Embed(title="🤖 ChatGPT mode 📝", description=text_output[0], color=discord.Color.gold()).set_footer(text=user_input), ephemeral=False)

### Code for /getuser ###
    @app_commands.command(name="getartist", description="Provides basic information of our members who use the bot")
    @app_commands.describe(discord_user="ElectraArt user within same server")
    async def getartist(self, interaction: discord.Interaction, discord_user: discord.Member):
        if str(interaction.guild_id) in self.WHITE_LISTED_SERVERS:
            await interaction.response.defer()
            # Log command user to database
            await UserApi.check_and_add_member(discoMember=interaction.user)
            # Update user profile 
            # Get user profile
            user_profile = await UserApi.get_user_info(discoMember=discord_user)

        if user_profile != "Error" and user_profile != "Failed":
            user_embed = discord.Embed(title="🎨 Artist Profile for: 🌟 {} 🌟".format(discord_user.name), color=discord.Color.gold())
            recent_art_guild = self.bot.get_guild(user_profile["recentArtSRC"])
            # Create embed
            if discord_user.avatar:
                user_embed.set_thumbnail(url=discord_user.avatar.url)
            user_embed.add_field(name="💡 Recently Created Art at:", value=recent_art_guild.name, inline=True)
            user_embed.add_field(name="↕️ Total Upvotes Points:", value=user_profile["upvotes"], inline=True)
            user_embed.set_footer(text="Proud creation of CJHackerz,\nmade with ❤️ in Python Programming and ASP.NET Core API using Neo4j Graph Database")
            await interaction.followup.send(embed=user_embed)
        else:
            user_embed = discord.Embed(title=":warning: :red_circle: Im Sorry Dave, Im Afraid I Can't Do That :red_circle: :warning:", description="User profile not found in database!", color=discord.Color.dark_orange())
            user_embed.set_footer(text="Proud creation of CJHackerz,\nmade with ❤️ in Python Programming and ASP.NET Core API using Neo4j Graph Database")
            logging.warning("=== User Profile Not Found ===")
            await interaction.followup.send(embed=user_embed)

### Code for /gettop10
    @app_commands.command(name="gettop10", description="Provides top 10 users with most upvotes")
    async def getuser(self, interaction: discord.Interaction):
        if str(interaction.guild_id) in self.WHITE_LISTED_SERVERS:
            await interaction.response.defer()
            # Log command user to database
            await UserApi.check_and_add_member(discoMember=interaction.user)
            # Update user profile 
            # Get user profile
            top10_list = await ScoreboardApi.get_top10_users()

        if top10_list != "Error" and top10_list != "Failed":
            top10_embed = discord.Embed(title="🎨 Top 10 Artists 🌟", color=discord.Color.red())
            # Create embed
            top10_embed.set_thumbnail(url="https://img.icons8.com/clouds/100/null/leaderboard.png")
            for i in range(10):
                top10_embed.add_field(name="🏆 Position {}:".format(i+1), value="`{}` with **{} points**".format(top10_list[i]["discoUserName"], top10_list[i]["upvotes"]), inline=True)
            top10_embed.set_footer(text="Proud creation of CJHackerz,\nmade with ❤️ in Python Programming and ASP.NET Core API using Neo4j Graph Database")
            await interaction.followup.send(embed=top10_embed)
            
### Code for /refresh
    # @app_commands.command(name="refresh", description="Refreshes art frame")
    # @app_commands.describe(discord_message="Art frame message ID")
    # async def refresh(self, interaction: discord.Interaction, discord_message: int):
    #     if str(interaction.guild_id) in self.WHITE_LISTED_SERVERS:
    #         art_frame = interaction.channel.fetch_message(discord_message)
    #         await interaction.response.defer()
    #         # Log command user to database
    #         await UserApi.check_and_add_member(discoMember=interaction.user)
    #         old_frame = art_frame.embeds
    #         old_frame_url = await ArtApi.get_art_url(art_frame)
    #         remote_file_name = old_frame_url.split("/")[-1].split("?")[0]
    #         new_frame_url = await ArtApi.refresh_art_url(art_frame, remote_file_name)
    #         old_frame[1].set_image(url=new_frame_url)
    #         await art_frame.edit(embeds=old_frame)
    #         await interaction.followup.send("Art frame refreshed!")

# Code for /genhelp command            
    @app_commands.command(name="genhelp", description="Displays command manual for the bot")
    async def genhelp(self, interaction: discord.Interaction):
        if str(interaction.guild_id) in self.WHITE_LISTED_SERVERS:

            help_embed = discord.Embed(title="ElectraArt User Manual", 
            description="This is help command, a commonly present feature in Discord bots that provides information to users on how to use the bot and its various commands. The purpose of this command is to give users a quick reference for the ElectraArt available commands, usage examples, and what they do.",
            color=discord.Colour.from_str("#22ff00"))
            help_embed.set_thumbnail(url="https://img.icons8.com/external-itim2101-lineal-color-itim2101/64/null/external-book-back-to-school-itim2101-lineal-color-itim2101.png")
            help_embed.add_field(name="/genimage user_input my creativity goes here", value="""
            Quickly provides one AI generated image based on text prompt from user who ran the command.

            To learn how to provide best quality prompts to generate desired images, please refer to following guide and download pdf e-book from there.
            https://dallery.gallery/the-dalle-2-prompt-book/
            """, inline=False)
            help_embed.add_field(name="/getuser", value="Shows the arist profile of discord user part of our database with basic info and upvotes received", inline=False)
            help_embed.add_field(name="/genhelp", value="Shows the ElectraArt User Manual and it's related commands", inline=False)
            help_embed.set_footer(text="Proud creation of CJHackerz,\nmade with ❤️ in Python Programming and ASP.NET Core API using Neo4j Graph Database")
            await interaction.response.send_message(embed=help_embed, ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Baseline(bot))