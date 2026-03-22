import discord
from discord.ext import commands
from discord import app_commands

INITIATIVE = {}

role_DM = "DM"

class Initiative(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="setinitiative", description="Set initiative")
    async def setInitiative(self, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=role_DM)
        if role is None or role not in interaction.user.roles:
            await interaction.response.send_message("You are not authorized to run this command.", ephemeral=True)
            return
        await interaction.response.send_message("Initiative Set")

    @app_commands.command(name="updateinitiative", description="Update initiative")
    async def updateInitiative(self, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=role_DM)
        if role is None or role not in interaction.user.roles:
            await interaction.response.send_message("You are not authorized to run this command.", ephemeral=True)
            return
        await interaction.response.send_message("Initiative Updated")

    @app_commands.command(name="initiative", description="Display initiative")
    async def Initiative(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Initiative",
            description="A list who is currently going/next in initiative"
        )
        await interaction.response.send_message(embed=embed)
        poll_message = await interaction.original_response()
        await poll_message.add_reaction("❌")
        await poll_message.add_reaction("➡️")

async def setup(bot):
    await bot.add_cog(Initiative(bot))