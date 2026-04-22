import unittest
import discord
import main 
# Using example code from pythondocs.org
class TestDiscordCommands(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')


    def test_roll(self):
        

if __name__ == "__main__":
    # Executing the unit testing script
    unittest.main()

