"""
Unit tests for the D&D Discord Bot commands.
Tests main.py, music.py, and initiative.py commands.
"""
import unittest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
import discord
from discord.ext import commands
import random
import pickle
import os
import sys

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_mock_interaction(guild_id=12345, user_id=11111, user_name="TestUser", has_voice=True, has_role=False):
    """Create a mock Discord interaction object."""
    interaction = MagicMock(spec=discord.Interaction)
    interaction.guild = MagicMock(spec=discord.Guild)
    interaction.guild.id = guild_id
    interaction.guild.roles = []
    interaction.guild.voice_client = None
    
    interaction.user = MagicMock(spec=discord.Member)
    interaction.user.id = user_id
    interaction.user.name = user_name
    interaction.user.roles = []
    
    if has_voice:
        interaction.user.voice = MagicMock(spec=discord.VoiceState)
        interaction.user.voice.channel = MagicMock(spec=discord.VoiceChannel)
        interaction.user.voice.channel.name = "Test Voice Channel"
    else:
        interaction.user.voice = None
    
    interaction.response = MagicMock()
    interaction.response.send_message = AsyncMock()
    interaction.response.defer = AsyncMock()
    interaction.original_response = AsyncMock()
    interaction.followup = MagicMock()
    interaction.followup.send = AsyncMock()
    
    return interaction


def create_mock_role(name="DM"):
    """Create a mock Discord role."""
    role = MagicMock(spec=discord.Role)
    role.name = name
    role.id = 99999
    return role

class TestMainCommands(unittest.IsolatedAsyncioTestCase):
    """Tests for commands in main.py"""
    
    def setUp(self):
        """Import main module and patch needed components."""
        import main
        self.main = main
        
    def create_interaction_with_role(self, role_name):
        """Create interaction with a specific role."""
        interaction = create_mock_interaction()
        role = create_mock_role(role_name)
        interaction.guild.roles = [role]
        interaction.user.roles = [role]
        return interaction, role
    
    def create_interaction_without_role(self):
        """Create interaction without DM or Player role."""
        interaction = create_mock_interaction()
        role = create_mock_role("DM")
        interaction.guild.roles = [role]
        interaction.user.roles = []
        return interaction
    
    # --- setDM Command Tests ---
    
    async def test_setDM_with_role_exists(self):
        """Test setDM command when DM role exists."""
        interaction, role = self.create_interaction_with_role("DM")
        
        await self.main.setDM.callback(self.main.setDM, interaction)
        
        interaction.user.add_roles.assert_called_once_with(role)
        interaction.response.send_message.assert_called_once()
    
    async def test_setDM_role_not_exists(self):
        """Test setDM command when DM role doesn't exist."""
        interaction = create_mock_interaction()
        interaction.guild.roles = []  # No roles
        
        await self.main.setDM.callback(self.main.setDM, interaction)
        
        interaction.response.send_message.assert_called_once_with("Role does not exist")
    
    # --- setPlayer Command Tests ---
    
    async def test_setPlayer_with_role_exists(self):
        """Test setPlayer command when Player role exists."""
        interaction, role = self.create_interaction_with_role("Player")
        
        await self.main.setPlayer.callback(self.main.setPlayer, interaction)
        
        interaction.user.add_roles.assert_called_once_with(role)
        interaction.response.send_message.assert_called_once()
    
    async def test_setPlayer_role_not_exists(self):
        """Test setPlayer command when Player role doesn't exist."""
        interaction = create_mock_interaction()
        interaction.guild.roles = []  # No roles
        
        await self.main.setPlayer.callback(self.main.setPlayer, interaction)
        
        interaction.response.send_message.assert_called_once_with("Role does not exist")
    
    # --- releaseDM Command Tests ---
    
    async def test_releaseDM_with_role(self):
        """Test releaseDM command when user has DM role."""
        interaction, role = self.create_interaction_with_role("DM")
        
        await self.main.releaseDM.callback(self.main.releaseDM, interaction)
        
        interaction.user.remove_roles.assert_called_once_with(role)
        interaction.response.send_message.assert_called_once()
    
    async def test_releaseDM_role_not_exists(self):
        """Test releaseDM command when DM role doesn't exist."""
        interaction = create_mock_interaction()
        interaction.guild.roles = []
        
        await self.main.releaseDM.callback(self.main.releaseDM, interaction)
        
        interaction.response.send_message.assert_called_once_with("Role does not exist")
    
    # --- releasePlayer Command Tests ---
    
    async def test_releasePlayer_with_role(self):
        """Test releasePlayer command when user has Player role."""
        interaction, role = self.create_interaction_with_role("Player")
        
        await self.main.releasePlayer.callback(self.main.releasePlayer, interaction)
        
        interaction.user.remove_roles.assert_called_once_with(role)
        interaction.response.send_message.assert_called_once()
    
    async def test_releasePlayer_role_not_exists(self):
        """Test releasePlayer command when Player role doesn't exist."""
        interaction = create_mock_interaction()
        interaction.guild.roles = []
        
        await self.main.releasePlayer.callback(self.main.releasePlayer, interaction)
        
        interaction.response.send_message.assert_called_once_with("Role does not exist")
    
    # --- roll Command Tests ---
    
    @patch("main.random.randint", return_value=4)
    async def test_roll_single_die(self, mock_randint):
        """Test rolling a single die."""
        interaction = create_mock_interaction()
        
        await self.main.roll.callback(self.main.roll, interaction, n=1, dn=6)
        
        interaction.response.send_message.assert_called_once_with("4")
        mock_randint.assert_called_once_with(1, 6)
    
    @patch("main.random.randint", return_value=3)
    async def test_roll_multiple_dice(self, mock_randint):
        """Test rolling multiple dice."""
        interaction = create_mock_interaction()
        
        await self.main.roll.callback(self.main.roll, interaction, n=3, dn=6)
        
        interaction.response.send_message.assert_called_once_with("3, 3, 3")
        self.assertEqual(mock_randint.call_count, 3)
    
    @patch("main.random.randint", side_effect=[1, 6, 3])
    async def test_roll_different_values(self, mock_randint):
        """Test rolling dice with different random values."""
        interaction = create_mock_interaction()
        
        await self.main.roll.callback(self.main.roll, interaction, n=3, dn=6)
        
        interaction.response.send_message.assert_called_once_with("1, 6, 3")
    
    @patch("main.random.randint", return_value=1)
    async def test_roll_one_sided_die(self, mock_randint):
        """Test rolling a one-sided die (always returns 1)."""
        interaction = create_mock_interaction()
        
        await self.main.roll.callback(self.main.roll, interaction, n=3, dn=1)
        
        interaction.response.send_message.assert_called_once_with("1, 1, 1")
    
    @patch("main.random.randint", return_value=20)
    async def test_roll_max_value(self, mock_randint):
        """Test rolling the maximum value on a die."""
        interaction = create_mock_interaction()
        
        await self.main.roll.callback(self.main.roll, interaction, n=1, dn=20)
        
        interaction.response.send_message.assert_called_once_with("20")
        mock_randint.assert_called_once_with(1, 20)

class TestMusicCommands(unittest.IsolatedAsyncioTestCase):
    """Tests for commands in music.py"""
    
    def setUp(self):
        """Import music module and create cog."""
        import music
        self.music_module = music
        
        # Create a mock bot
        self.bot = MagicMock()
        self.bot.user = MagicMock()
        self.bot.user.id = 12345
        
        # Create Music cog
        self.music_cog = music.Music(self.bot)
    
    def create_interaction(self, has_voice=True, guild_id=12345):
        """Create a mock interaction for music commands."""
        interaction = create_mock_interaction(guild_id=guild_id, has_voice=has_voice)
        interaction.guild.voice_client = None
        return interaction
    
    # --- join Command Tests ---
    
    async def test_join_in_voice_channel(self):
        """Test join command when user is in a voice channel."""
        interaction = self.create_interaction(has_voice=True)
        interaction.guild.voice_client = None
        
        await self.music_cog.join.callback(self.music_cog, interaction)
        
        interaction.response.send_message.assert_called_once()
        call_args = interaction.response.send_message.call_args
        self.assertIn("Joined", str(call_args))
    
    async def test_join_not_in_voice_channel(self):
        """Test join command when user is not in a voice channel."""
        interaction = self.create_interaction(has_voice=False)
        
        await self.music_cog.join.callback(self.music_cog, interaction)
        
        interaction.response.send_message.assert_called_once()
        call_args = interaction.response.send_message.call_args
        self.assertIn("not in a voice channel", str(call_args).lower())
    
    async def test_join_dm_context(self):
        """Test join command when used in DM (should fail)."""
        interaction = self.create_interaction()
        interaction.guild = None  # DM context
        
        await self.music_cog.join.callback(self.music_cog, interaction)
        
        interaction.response.send_message.assert_called_once()
        call_args = interaction.response.send_message.call_args
        self.assertIn("server", str(call_args).lower())
    
    # --- leave Command Tests ---
    
    async def test_leave_connected_to_voice(self):
        """Test leave command when bot is in a voice channel."""
        interaction = self.create_interaction()
        
        # Mock voice client
        mock_vc = MagicMock()
        interaction.guild.voice_client = mock_vc
        
        await self.music_cog.leave.callback(self.music_cog, interaction)
        
        mock_vc.disconnect.assert_called_once()
        interaction.response.send_message.assert_called_once()
    
    async def test_leave_not_connected(self):
        """Test leave command when bot is not in a voice channel."""
        interaction = self.create_interaction()
        interaction.guild.voice_client = None
        
        await self.music_cog.leave.callback(self.music_cog, interaction)
        
        interaction.response.send_message.assert_called_once()
        call_args = interaction.response.send_message.call_args
        self.assertIn("not in a voice channel", str(call_args).lower())
    
    # --- stop Command Tests ---
    
    async def test_stop_playing(self):
        """Test stop command when audio is playing."""
        interaction = self.create_interaction()
        
        # Mock voice client with playing audio
        mock_vc = MagicMock()
        mock_vc.is_playing.return_value = True
        interaction.guild.voice_client = mock_vc
        
        await self.music_cog.stop.callback(self.music_cog, interaction)
        
        mock_vc.stop.assert_called_once()
        interaction.response.send_message.assert_called_once()
    
    async def test_stop_not_playing(self):
        """Test stop command when nothing is playing."""
        interaction = self.create_interaction()
        
        # Mock voice client without playing audio
        mock_vc = MagicMock()
        mock_vc.is_playing.return_value = False
        interaction.guild.voice_client = mock_vc
        
        await self.music_cog.stop.callback(self.music_cog, interaction)
        
        mock_vc.stop.assert_not_called()
        interaction.response.send_message.assert_called_once()
        call_args = interaction.response.send_message.call_args
        self.assertIn("Nothing is playing", str(call_args))
    
    # --- pause Command Tests ---
    
    async def test_pause_playing(self):
        """Test pause command when audio is playing."""
        interaction = self.create_interaction()
        
        # Mock voice client with playing audio
        mock_vc = MagicMock()
        mock_vc.is_playing.return_value = True
        interaction.guild.voice_client = mock_vc
        
        await self.music_cog.pause.callback(self.music_cog, interaction)
        
        mock_vc.pause.assert_called_once()
        interaction.response.send_message.assert_called_once()
    
    async def test_pause_not_playing(self):
        """Test pause command when nothing is playing."""
        interaction = self.create_interaction()
        
        mock_vc = MagicMock()
        mock_vc.is_playing.return_value = False
        interaction.guild.voice_client = mock_vc
        
        await self.music_cog.pause.callback(self.music_cog, interaction)
        
        mock_vc.pause.assert_not_called()
        interaction.response.send_message.assert_called_once()
    
    # --- resume Command Tests ---
    
    async def test_resume_paused(self):
        """Test resume command when audio is paused."""
        interaction = self.create_interaction()
        
        mock_vc = MagicMock()
        mock_vc.is_paused.return_value = True
        interaction.guild.voice_client = mock_vc
        
        await self.music_cog.resume.callback(self.music_cog, interaction)
        
        mock_vc.resume.assert_called_once()
        interaction.response.send_message.assert_called_once()
    
    async def test_resume_not_paused(self):
        """Test resume command when nothing is paused."""
        interaction = self.create_interaction()
        
        mock_vc = MagicMock()
        mock_vc.is_paused.return_value = False
        interaction.guild.voice_client = mock_vc
        
        await self.music_cog.resume.callback(self.music_cog, interaction)
        
        mock_vc.resume.assert_not_called()
        interaction.response.send_message.assert_called_once()
    
    # --- play Command Tests ---
    
    async def test_play_not_in_voice_channel(self):
        """Test play command when user is not in a voice channel."""
        interaction = self.create_interaction(has_voice=False)
        
        await self.music_cog.play.callback(self.music_cog, interaction, url="https://youtube.com/test")
        
        interaction.response.send_message.assert_called_once()
        call_args = interaction.response.send_message.call_args
        self.assertIn("need to be in a voice channel", str(call_args).lower())
    
    async def test_play_dm_context(self):
        """Test play command when used in DM (should fail)."""
        interaction = self.create_interaction()
        interaction.guild = None
        
        await self.music_cog.play.callback(self.music_cog, interaction, url="https://youtube.com/test")
        
        interaction.response.send_message.assert_called_once()
        call_args = interaction.response.send_message.call_args
        self.assertIn("server", str(call_args).lower())

class TestInitiativeCommands(unittest.IsolatedAsyncioTestCase):
    """Tests for commands in initiative.py"""
    
    def setUp(self):
        """Import initiative module and create cog."""
        import initiative
        self.initiative_module = initiative
        
        # Create a mock bot
        self.bot = MagicMock()
        self.bot.user = MagicMock()
        self.bot.user.id = 12345
        
        # Create Initiative cog
        self.initiative_cog = initiative.Initiative(self.bot)
    
    def create_interaction(self, guild_id=12345, user_id=11111, has_dm_role=False):
        """Create a mock interaction for initiative commands."""
        interaction = create_mock_interaction(guild_id=guild_id, user_id=user_id)
        
        if has_dm_role:
            dm_role = create_mock_role("DM")
            interaction.guild.roles = [dm_role]
            interaction.user.roles = [dm_role]
        else:
            interaction.guild.roles = [create_mock_role("DM")]
            interaction.user.roles = []
        
        return interaction
    
    # --- setInitiative Command Tests ---
    
    async def test_setInitiative_success(self):
        """Test setInitiative command with valid input."""
        interaction = self.create_interaction(has_dm_role=True)
        
        await self.initiative_cog.setInitiative.callback(
            self.initiative_cog, 
            interaction, 
            characters="Alice:18, Goblin:14"
        )
        
        interaction.response.send_message.assert_called_once()
        # Check that initiative was set
        self.assertIn(interaction.guild.id, self.initiative_cog.initiative_state)
    
    async def test_setInitiative_no_dm_role(self):
        """Test setInitiative command without DM role."""
        interaction = self.create_interaction(has_dm_role=False)
        
        await self.initiative_cog.setInitiative.callback(
            self.initiative_cog,
            interaction,
            characters="Alice:18"
        )
        
        interaction.response.send_message.assert_called_once()
        call_args = interaction.response.send_message.call_args
        self.assertIn("not authorized", str(call_args).lower())
    
    async def test_setInitiative_invalid_format(self):
        """Test setInitiative command with invalid format."""
        interaction = self.create_interaction(has_dm_role=True)
        
        await self.initiative_cog.setInitiative.callback(
            self.initiative_cog,
            interaction,
            characters="Alice"  # Missing initiative value
        )
        
        interaction.response.send_message.assert_called_once()
    
    async def test_setInitiative_dm_context(self):
        """Test setInitiative in DM context (should fail)."""
        interaction = self.create_interaction()
        interaction.guild = None
        
        await self.initiative_cog.setInitiative.callback(
            self.initiative_cog,
            interaction,
            characters="Alice:18"
        )
        
        interaction.response.send_message.assert_called_once()
    
    # --- updateInitiative Command Tests ---
    
    async def test_updateInitiative_success(self):
        """Test updateInitiative command with valid input."""
        interaction = self.create_interaction(has_dm_role=True)
        guild_id = interaction.guild.id
        
        # First set some initiative
        self.initiative_cog.initiative_state[guild_id] = {
            "order": [{"name": "Alice", "initiative": 18}],
            "characters": {"Alice": 18},
            "current_index": 0,
            "message_id": None
        }
        
        await self.initiative_cog.updateInitiative.callback(
            self.initiative_cog,
            interaction,
            name="Alice",
            initiative=20
        )
        
        interaction.response.send_message.assert_called_once()
    
    async def test_updateInitiative_no_initiative_set(self):
        """Test updateInitiative when no initiative is set."""
        interaction = self.create_interaction(has_dm_role=True)
        
        await self.initiative_cog.updateInitiative.callback(
            self.initiative_cog,
            interaction,
            name="Alice",
            initiative=18
        )
        
        interaction.response.send_message.assert_called_once()
        call_args = interaction.response.send_message.call_args
        self.assertIn("not been set", str(call_args).lower())
    
    async def test_updateInitiative_character_not_found(self):
        """Test updateInitiative when character doesn't exist."""
        interaction = self.create_interaction(has_dm_role=True)
        guild_id = interaction.guild.id
        
        # Set initiative without the character
        self.initiative_cog.initiative_state[guild_id] = {
            "order": [{"name": "Bob", "initiative": 15}],
            "characters": {"Bob": 15},
            "current_index": 0,
            "message_id": None
        }
        
        await self.initiative_cog.updateInitiative.callback(
            self.initiative_cog,
            interaction,
            name="Alice",  # Not in the list
            initiative=18
        )
        
        interaction.response.send_message.assert_called_once()
        call_args = interaction.response.send_message.call_args
        self.assertIn("not in the initiative", str(call_args).lower())
    
    async def test_updateInitiative_remove_character(self):
        """Test updateInitiative to remove a character (initiative=0)."""
        interaction = self.create_interaction(has_dm_role=True)
        guild_id = interaction.guild.id
        
        # Set initiative with character
        self.initiative_cog.initiative_state[guild_id] = {
            "order": [{"name": "Alice", "initiative": 18}],
            "characters": {"Alice": 18},
            "current_index": 0,
            "message_id": None
        }
        
        await self.initiative_cog.updateInitiative.callback(
            self.initiative_cog,
            interaction,
            name="Alice",
            initiative=0  # Remove character
        )
        
        interaction.response.send_message.assert_called_once()
    
    # --- rollInitiative Command Tests ---
    
    @patch("initiative.random.randint", return_value=15)
    async def test_rollInitiative_with_modifier(self, mock_randint):
        """Test rollInitiative with a modifier."""
        interaction = self.create_interaction()
        
        await self.initiative_cog.rollInitiative.callback(
            self.initiative_cog,
            interaction,
            name="Alice",
            modifier=5,
            add_to_list=False
        )
        
        interaction.response.send_message.assert_called_once()
        call_args = interaction.response.send_message.call_args
        self.assertIn("20", str(call_args))  # 15 + 5 = 20
    
    @patch("initiative.random.randint", return_value=10)
    async def test_rollInitiative_default_modifier(self, mock_randint):
        """Test rollInitiative with default (None) modifier."""
        interaction = self.create_interaction()
        
        await self.initiative_cog.rollInitiative.callback(
            self.initiative_cog,
            interaction,
            name="Alice",
            modifier=None,
            add_to_list=False
        )
        
        interaction.response.send_message.assert_called_once()
    
    async def test_rollInitiative_dm_context(self):
        """Test rollInitiative in DM context (should fail)."""
        interaction = self.create_interaction()
        interaction.guild = None
        
        await self.initiative_cog.rollInitiative.callback(
            self.initiative_cog,
            interaction,
            name="Alice",
            modifier=5
        )
        
        interaction.response.send_message.assert_called_once()
    
    # --- Initiative (display) Command Tests ---
    
    async def test_initiative_display_success(self):
        """Test initiative display command."""
        interaction = self.create_interaction(has_dm_role=True)
        guild_id = interaction.guild.id
        
        # Set initiative
        self.initiative_cog.initiative_state[guild_id] = {
            "order": [{"name": "Alice", "initiative": 18}, {"name": "Bob", "initiative": 15}],
            "characters": {"Alice": 18, "Bob": 15},
            "current_index": 0,
            "message_id": None
        }
        
        # Mock the original_response to return a mock message
        mock_message = MagicMock()
        mock_message.id = 12345
        mock_message.add_reaction = AsyncMock()
        interaction.original_response = AsyncMock(return_value=mock_message)
        
        await self.initiative_cog.Initiative.callback(self.initiative_cog, interaction)
        
        interaction.response.send_message.assert_called_once()
    
    async def test_initiative_display_no_initiative(self):
        """Test initiative display when nothing is set."""
        interaction = self.create_interaction(has_dm_role=True)
        
        await self.initiative_cog.Initiative.callback(self.initiative_cog, interaction)
        
        interaction.response.send_message.assert_called_once()
        call_args = interaction.response.send_message.call_args
        self.assertIn("not been set", str(call_args).lower())
    
    # --- Helper Method Tests ---
    
    def test_parse_initiative_entries_valid(self):
        """Test _parse_initiative_entries with valid input."""
        result = self.initiative_cog._parse_initiative_entries("Alice:18, Bob:15, Charlie:20")
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["name"], "Charlie")  # Highest initiative first
        self.assertEqual(result[0]["initiative"], 20)
    
    def test_parse_initiative_entries_empty(self):
        """Test _parse_initiative_entries with empty input."""
        with self.assertRaises(ValueError):
            self.initiative_cog._parse_initiative_entries("")
    
    def test_parse_initiative_entries_invalid_format(self):
        """Test _parse_initiative_entries with invalid format."""
        with self.assertRaises(ValueError):
            self.initiative_cog._parse_initiative_entries("Alice")  # No colon
    
    def test_parse_initiative_entries_invalid_initiative(self):
        """Test _parse_initiative_entries with non-numeric initiative."""
        with self.assertRaises(ValueError):
            self.initiative_cog._parse_initiative_entries("Alice:abc")
    
    def test_format_modifier_zero(self):
        """Test _format_modifier with zero."""
        result = self.initiative_cog._format_modifier(0)
        self.assertEqual(result, "")
    
    def test_format_modifier_positive(self):
        """Test _format_modifier with positive number."""
        result = self.initiative_cog._format_modifier(5)
        self.assertIn("+", result)
        self.assertIn("5", result)
    
    def test_format_modifier_negative(self):
        """Test _format_modifier with negative number."""
        result = self.initiative_cog._format_modifier(-3)
        self.assertIn("-", result)
        self.assertIn("3", result)
    
    def test_upsert_initiative_entry_new(self):
        """Test _upsert_initiative_entry with new character."""
        guild_id = 12345
        
        self.initiative_cog._upsert_initiative_entry(guild_id, "Alice", 18)
        
        self.assertIn(guild_id, self.initiative_cog.initiative_state)
        self.assertIn("Alice", self.initiative_cog.initiative_state[guild_id]["characters"])
    
    def test_upsert_initiative_entry_update(self):
        """Test _upsert_initiative_entry with existing character."""
        guild_id = 12345
        
        # Add first character
        self.initiative_cog._upsert_initiative_entry(guild_id, "Alice", 18)
        # Update existing character
        self.initiative_cog._upsert_initiative_entry(guild_id, "Alice", 20)
        
        self.assertEqual(
            self.initiative_cog.initiative_state[guild_id]["characters"]["Alice"],
            20
        )
    
    def test_build_initiative_embed(self):
        """Test _build_initiative_embed."""
        guild_id = 12345
        self.initiative_cog.initiative_state[guild_id] = {
            "order": [{"name": "Alice", "initiative": 18}, {"name": "Bob", "initiative": 15}],
            "characters": {"Alice": 18, "Bob": 15},
            "current_index": 0,
            "message_id": None
        }
        
        embed = self.initiative_cog._build_initiative_embed(guild_id)
        
        self.assertEqual(embed.title, "Initiative")
        self.assertIn("Alice", embed.description)
        self.assertIn("Bob", embed.description)

if __name__ == "__main__":
    unittest.main()