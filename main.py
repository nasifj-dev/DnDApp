import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from Stats.pdftocharacter import pdftosheet
from pypdf import PdfReader
import pickle
import random


load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True
intents.guilds = True

bot = commands.Bot(command_prefix='/', intents=intents)

role_DM = "DM"
role_Player = "Player"

@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")
    try:
        await bot.load_extension("music")
        await bot.load_extension("initiative")
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

# Role Commands
@bot.tree.command(name="setdm", description="Give yourself the DM role")
async def setDM(interaction: discord.Interaction):
    role = discord.utils.get(interaction.guild.roles, name=role_DM)
    if role:
        await interaction.user.add_roles(role)
        await interaction.response.send_message(f"{interaction.user.mention} is now assigned to {role_DM}", ephemeral = True)
    else:
        await interaction.response.send_message("Role does not exist")

@bot.tree.command(name="setplayer", description="Give yourself the Player role")
async def setPlayer(interaction: discord.Interaction):
    role = discord.utils.get(interaction.guild.roles, name=role_Player)
    if role:
        await interaction.user.add_roles(role)
        await interaction.response.send_message(f"{interaction.user.mention} is now assigned to {role_Player}", ephemeral = True)
    else:
        await interaction.response.send_message("Role does not exist")

@bot.tree.command(name="releasedm", description="Release yourself of the DM role")
async def releaseDM(interaction: discord.Interaction):
    role = discord.utils.get(interaction.guild.roles, name=role_DM)
    if role:
        await interaction.user.remove_roles(role)
        await interaction.response.send_message(f"{interaction.user.mention} is now removed from {role_DM}", ephemeral = True)
    else:
        await interaction.response.send_message("Role does not exist")

@bot.tree.command(name="releaseplayer", description="Release yourself of the Player role")
async def releasePlayer(interaction: discord.Interaction):
    role = discord.utils.get(interaction.guild.roles, name=role_Player)
    if role:
        await interaction.user.remove_roles(role)
        await interaction.response.send_message(f"{interaction.user.mention} is now removed from {role_Player}", ephemeral = True)
    else:
        await interaction.response.send_message("Role does not exist")

@bot.tree.command(name="uploadsheet", description="Upload a character sheets")
async def uploadSheet(interaction: discord.Interaction, sheet: discord.Attachment):
    try:
        await sheet.save(f"Sheets/{sheet.filename}")
        reader = PdfReader(f"Sheets/{sheet.filename}")
        pages = []
        for num, page in enumerate(reader.pages):
            extract = page.extract_text().split("\n")
            pages.append(extract)
        first, second, last = pages[0], pages[1], pages[-1]
        char = pdftosheet(first, second, last)

        with open("charactersPickle", "rb") as fin:
            try:
                char_list = pickle.load(fin)
            except EOFError:
                char_list = {}
        char_list[interaction.user.name] = char
        with open("charactersPickle", "wb") as dbfile:
            pickle.dump(char_list, dbfile)

        await interaction.response.send_message(f'You have uploaded {char}')
    except Exception as e:
        await interaction.response.send_message(f'{e}')

@bot.tree.command(name="abilitycheck", description="Set an ability check")
async def abilityCheck(interaction: discord.Interaction):
    pass

@bot.tree.command(name="rolldie",description="Rolls dice in a NdN format")
async def roll(interaction: discord.Interaction, n: int, dn: int):
    """Rolls a dice in NdN format"""

    # Parsing the result into a N, N, N format
    result = ', '.join(str(random.randint(1, dn)) for r in range(n))
    await interaction.response.send_message(result)


# Run Bot
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
