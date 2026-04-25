import unittest
from discord.ext import commands
import discord
import main 
from unittest.mock import AsyncMock, MagicMock, patch 

def make_interaction():
    interaction = MagicMock(spec=discord.Interaction)
    interaction.response = MagicMock()
    interaction.response.send_message = AsyncMock()
    return interaction

class TestRollDieCommand(unittest.IsolatedAsyncioTestCase):
    
    @patch("main.random.randint", return_value=4) # Force it to return a value of 4
    async def test_roll_single_die(self, mock_randint):
        interaction = make_interaction()

        await main.roll.callback(interaction, n=1, dn=6)

        interaction.response.send_message.assert_called_once_with("4")
        mock_randint.assert_called_once_with(1, 6)

    @patch("main.random.randint", return_value=3) # Force it to return a value of 3
    async def test_roll_multiple_dice(self, mock_randint):
        interaction = make_interaction() # Creating another discord interaction
        
        await main.roll.callback(interaction, n=3, dn=6)

        # All 3 die rolls return 3 (patched), expecting "3, 3, 3"
        interaction.response.send_message.assert_called_once_with("3, 3, 3")
        self.assertEqual(mock_randint.call_count, 3)

    @patch("main.random.randint", side_effect=[1, 20])
    async def test_roll_different_values(self, mock_randint):
        interaction = make_interaction()

        await main.roll.callback(interaction, n=2, dn=20)

        interaction.response.send_message_assert_called_once_with("1, 20")

    @patch("main.random.randint", return_value=1) # <-- Forcing a return value of 1
    async def test_roll_one_sided_die(self, mock_randint):
        # dn=1 should always return 1
        interaction = make_interaction()

        await main.roll.callback(interaction, n=3, dn=1)

        interaction.response.send_message.assert_called_once_with("1, 1, 1")

if __name__ == "__main__":
    # Executing the unit testing script
    unittest.main()