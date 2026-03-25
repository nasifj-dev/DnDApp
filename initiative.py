import discord
from discord.ext import commands
from discord import app_commands
import random

role_DM = "DM"
CROSS_MARK = "\N{CROSS MARK}"
NEXT_ARROW = "\N{BLACK RIGHTWARDS ARROW}"


class Initiative(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.initiative_state = {}

    @app_commands.command(name="setinitiative", description="Set initiative")
    @app_commands.describe(
        characters="Comma-separated list like: Alice:18, Goblin 1:14, Goblin 2:12"
    )
    async def setInitiative(self, interaction: discord.Interaction, characters: str):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        role = discord.utils.get(interaction.guild.roles, name=role_DM)
        if role is None or role not in interaction.user.roles:
            await interaction.response.send_message("You are not authorized to run this command.", ephemeral=True)
            return

        try:
            entries = self._parse_initiative_entries(characters)
        except ValueError as exc:
            await interaction.response.send_message(str(exc), ephemeral=True)
            return

        guild_id = interaction.guild.id
        self.initiative_state[guild_id] = {
            "order": entries,
            "characters": {entry["name"]: entry["initiative"] for entry in entries},
            "current_index": 0,
            "message_id": None,
        }

        await interaction.response.send_message("Initiative set.", ephemeral=True)

    @app_commands.command(name="updateinitiative", description="Update initiative")
    @app_commands.describe(
        name="Character name to update",
        initiative="New initiative value"
    )
    async def updateInitiative(self, interaction: discord.Interaction, name: str, initiative: int):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        role = discord.utils.get(interaction.guild.roles, name=role_DM)
        if role is None or role not in interaction.user.roles:
            await interaction.response.send_message("You are not authorized to run this command.", ephemeral=True)
            return

        guild_id = interaction.guild.id
        state = self.initiative_state.get(guild_id)
        if state is None:
            await interaction.response.send_message("No initiative has been set for this server yet.", ephemeral=True)
            return

        if name not in state["characters"]:
            await interaction.response.send_message(f"{name} is not in the initiative tracker.", ephemeral=True)
            return

        current_name = None
        if state["order"]:
            current_name = state["order"][state["current_index"]]["name"]

        if initiative == 0:
            del state["characters"][name]
            state["order"] = [entry for entry in state["order"] if entry["name"] != name]

            if not state["order"]:
                state["current_index"] = 0
                await interaction.response.send_message(f"{name} was removed from initiative.", ephemeral=True)
                return

            if current_name == name:
                state["current_index"] %= len(state["order"])
            else:
                for index, entry in enumerate(state["order"]):
                    if entry["name"] == current_name:
                        state["current_index"] = index
                        break
                else:
                    state["current_index"] = 0

            await interaction.response.send_message(f"{name} was removed from initiative.", ephemeral=True)
            return

        state["characters"][name] = initiative
        for entry in state["order"]:
            if entry["name"] == name:
                entry["initiative"] = initiative
                break

        state["order"].sort(key=lambda entry: entry["initiative"], reverse=True)
        for index, entry in enumerate(state["order"]):
            if entry["name"] == current_name:
                state["current_index"] = index
                break
        else:
            state["current_index"] = min(state["current_index"], len(state["order"]) - 1)

        await interaction.response.send_message("Initiative updated.", ephemeral=True)

    @app_commands.command(name="rollinitiative", description="Roll initiative and optionally add it to the tracker")
    @app_commands.describe(
        name="Character name to roll for",
        modifier="Initiative modifier to add to the d20 roll",
        add_to_list="If true, add or update this character in the initiative tracker"
    )
    async def rollInitiative(
        self,
        interaction: discord.Interaction,
        name: str,
        modifier: int = 0,
        add_to_list: bool = True
    ):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        roll = random.randint(1, 20)
        total = roll + modifier
        guild_id = interaction.guild.id

        if add_to_list:
            self._upsert_initiative_entry(guild_id, name, total)

        add_text = " and added to initiative" if add_to_list else ""
        await interaction.response.send_message(
            f"{name} rolled `{roll}`"
            f"{self._format_modifier(modifier)}"
            f" for a total of `{total}`{add_text}.",
            ephemeral=True
        )

    @app_commands.command(name="initiative", description="Display initiative")
    async def Initiative(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        guild_id = interaction.guild.id
        if guild_id not in self.initiative_state:
            await interaction.response.send_message("No initiative has been set for this server yet.", ephemeral=True)
            return

        embed = self._build_initiative_embed(guild_id)
        await interaction.response.send_message(embed=embed)
        poll_message = await interaction.original_response()
        self.initiative_state[guild_id]["message_id"] = poll_message.id
        await poll_message.add_reaction(CROSS_MARK)
        await poll_message.add_reaction(NEXT_ARROW)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.guild_id is None or payload.user_id == self.bot.user.id:
            return

        state = self.initiative_state.get(payload.guild_id)
        if state is None or payload.message_id != state.get("message_id"):
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        member = guild.get_member(payload.user_id)
        if member is None or member.bot:
            return

        emoji = str(payload.emoji)
        channel = self.bot.get_channel(payload.channel_id)
        if channel is None:
            channel = await self.bot.fetch_channel(payload.channel_id)

        message = await channel.fetch_message(payload.message_id)

        if emoji == CROSS_MARK:
            await message.delete()
            state["message_id"] = None
            return

        if emoji != NEXT_ARROW:
            return

        if not state["order"]:
            await message.delete()
            state["message_id"] = None
            return

        state["current_index"] = (state["current_index"] + 1) % len(state["order"])
        await message.delete()
        new_message = await channel.send(embed=self._build_initiative_embed(payload.guild_id))
        state["message_id"] = new_message.id
        await new_message.add_reaction(CROSS_MARK)
        await new_message.add_reaction(NEXT_ARROW)

    def _parse_initiative_entries(self, characters: str):
        entries = []
        raw_entries = [entry.strip() for entry in characters.split(",") if entry.strip()]
        if not raw_entries:
            raise ValueError("Please provide at least one character.")

        for raw_entry in raw_entries:
            if ":" not in raw_entry:
                raise ValueError(
                    "Each character must be formatted like `Name:Initiative`. "
                    "Example: `Alice:18, Goblin 1:14`"
                )

            name_part, initiative_part = raw_entry.rsplit(":", 1)
            name = name_part.strip()
            if not name:
                raise ValueError("Each character needs a name before the `:`.")

            try:
                initiative = int(initiative_part.strip())
            except ValueError as exc:
                raise ValueError(f"Initiative for `{name}` must be a whole number.") from exc

            entries.append({"name": name, "initiative": initiative})

        entries.sort(key=lambda entry: entry["initiative"], reverse=True)
        return entries

    def _upsert_initiative_entry(self, guild_id: int, name: str, initiative: int):
        state = self.initiative_state.setdefault(
            guild_id,
            {
                "order": [],
                "characters": {},
                "current_index": 0,
                "message_id": None,
            }
        )

        current_name = None
        if state["order"]:
            current_name = state["order"][state["current_index"]]["name"]

        if name in state["characters"]:
            for entry in state["order"]:
                if entry["name"] == name:
                    entry["initiative"] = initiative
                    break
        else:
            state["order"].append({"name": name, "initiative": initiative})

        state["characters"][name] = initiative
        state["order"].sort(key=lambda entry: entry["initiative"], reverse=True)

        if current_name is None:
            state["current_index"] = 0
            return

        for index, entry in enumerate(state["order"]):
            if entry["name"] == current_name:
                state["current_index"] = index
                return

        state["current_index"] = 0

    def _format_modifier(self, modifier: int):
        if modifier == 0:
            return ""
        if modifier > 0:
            return f" + `{modifier}`"
        return f" - `{abs(modifier)}`"

    def _build_initiative_embed(self, guild_id: int):
        state = self.initiative_state[guild_id]
        order = state["order"]
        current_index = state["current_index"]

        description_lines = []
        for index, entry in enumerate(order):
            prefix = "->" if index == current_index else "  "
            description_lines.append(f"{prefix} **{entry['name']}** ({entry['initiative']})")

        embed = discord.Embed(
            title="Initiative",
            description="\n".join(description_lines)
        )
        return embed


async def setup(bot):
    await bot.add_cog(Initiative(bot))
