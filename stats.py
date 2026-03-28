from pdftocharacter import pdftosheet
import discord
from discord.ext import commands
from discord import app_commands
from pypdf import PdfReader
import pickle
from typing import Literal

class Stats(commands.Cog):
    """A collection of commands for handling character statistics."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="uploadsheet", description="Upload a character sheets")
    async def uploadSheet(self, interaction: discord.Interaction, sheet: discord.Attachment):
        """Upload a character sheet PDF and parse it into a Character object. Only users with the Player role can use this command. The character data is stored in a pickle file keyed by the user's name."""
        role = discord.utils.get(interaction.guild.roles, name="Player")
        if role is None or role not in interaction.user.roles:
            await interaction.response.send_message("You are not authorized to run this command.", ephemeral=True)
            return
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
            await interaction.response.send_message(f'{e}', ephemeral=True)

    @app_commands.command(name="abilitycheck", description="Set an ability check")
    async def abilityCheck(self, interaction: discord.Interaction, player: discord.User, 
                        ability: Literal['Acrobatics', 'Animal Handling', 'Arcana', 'Athletics', 'Deception', 
                                            'History', 'Insight', 'Intimidation', 'Investigation','Medicine', 'Nature', 
                                            'Perception', 'Performance', 'Persuasion','Religion','Sleight of Hand', 
                                            'Stealth', 'Survival',"STR", "DEX", "CON", "INT", "WIS", "CHA"], dc:int = 0):
        """Create an embed for an ability check and add a dice reaction for players to respond. Only users with the DM role can use this command."""
        role = discord.utils.get(interaction.guild.roles, name="DM")
        if role is None or role not in interaction.user.roles:
            await interaction.response.send_message("You are not authorized to run this command.", ephemeral=True)
            return
        if dc:
            score = f" DC {dc} "
        elif ability[0] in ['AEIOU']:
            score = "n "
        else:
            score = " "
        embed = discord.Embed(
            title=f"{ability} Check",
            description=f"{player.mention} must make a{score}{ability} check"
        )
        await interaction.response.send_message(embed=embed)
        poll_message = await interaction.original_response()
        await poll_message.add_reaction("🎲")

    @app_commands.command(name="skillmod", description="Get a stat from your character sheet")
    async def skillMod(self, interaction: discord.Interaction, 
                    ability: Literal['Acrobatics', 'Animal Handling', 'Arcana', 'Athletics', 'Deception', 
                                        'History', 'Insight', 'Intimidation', 'Investigation','Medicine', 'Nature', 
                                        'Perception', 'Performance', 'Persuasion','Religion','Sleight of Hand', 
                                        'Stealth', 'Survival']):
        """Get the skill modifier for a specified skill from the user's character sheet. The skill must be one of the standard D&D 5e skills. The character data is loaded from the pickle file based on the user's name."""
        with open("charactersPickle", "rb") as fin:
                try:
                    char_list = pickle.load(fin)
                except EOFError:
                    char_list = {}
        your_ch = char_list[interaction.user.name]
        await interaction.response.send_message(f"{your_ch.skill(ability)}")
    
    @app_commands.command(name="battlestats", description="Get all the stats you need for battle")
    async def battleStats(self, interaction: discord.Interaction):
        """Get the current HP, AC, and speed from the user's character sheet. The character data is loaded from the pickle file based on the user's name."""
        with open("charactersPickle", "rb") as fin:
                try:
                    char_list = pickle.load(fin)
                except EOFError:
                    char_list = {}
        your_ch = char_list[interaction.user.name]
        await interaction.response.send_message(f"{your_ch.battle_stats()}")

    @app_commands.command(name="damage", description="You got hurt!")
    async def damage(self, interaction: discord.Interaction, hitpoints: int):
        """Apply damage to the user's character and update the character sheet. The character data is loaded from the pickle file based on the user's name, modified with the damage, and then saved back to the pickle file."""
        with open("charactersPickle", "rb") as fin:
                try:
                    char_list = pickle.load(fin)
                except EOFError:
                    char_list = {}
        your_ch = char_list[interaction.user.name]

        await interaction.response.send_message(f"{your_ch.damage(hitpoints)}")

        char_list[interaction.user.name] = your_ch
        with open("charactersPickle", "wb") as dbfile:
                pickle.dump(char_list, dbfile)

    @app_commands.command(name="heal", description="Recover some health")
    async def heal(self, interaction: discord.Interaction, hitpoints: int):
        """Heal the user's character and update the character sheet. The character data is loaded from the pickle file based on the user's name, modified with the healing, and then saved back to the pickle file."""
        with open("charactersPickle", "rb") as fin:
                try:
                    char_list = pickle.load(fin)
                except EOFError:
                    char_list = {}
        your_ch = char_list[interaction.user.name]

        await interaction.response.send_message(f"{your_ch.heal(hitpoints)}")

        char_list[interaction.user.name] = your_ch
        with open("charactersPickle", "wb") as dbfile:
                pickle.dump(char_list, dbfile)

    @app_commands.command(name="inventory", description="Check your inventory")
    async def inventory(self, interaction: discord.Interaction):
        """Get the inventory list from the user's character sheet. The character data is loaded from the pickle file based on the user's name."""
        with open("charactersPickle", "rb") as fin:
                try:
                    char_list = pickle.load(fin)
                except EOFError:
                    char_list = {}
        your_ch = char_list[interaction.user.name]

        await interaction.response.send_message(f"{your_ch.inventory()}")

    @app_commands.command(name="spells", description="Check your spells")
    async def spells(self, interaction: discord.Interaction):
        """Get the spell list from the user's character sheet. The character data is loaded from the pickle file based on the user's name."""
        with open("charactersPickle", "rb") as fin:
                try:
                    char_list = pickle.load(fin)
                except EOFError:
                    char_list = {}
        your_ch = char_list[interaction.user.name]

        await interaction.response.send_message(f"{your_ch.spells()}")


async def setup(bot):
    await bot.add_cog(Stats(bot))