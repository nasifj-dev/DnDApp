import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp

FFMPEG_PATH = r"ffmpeg\ffmpeg.exe"

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

YDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True
}


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="join", description="Join your voice channel")
    async def join(self, interaction: discord.Interaction):
        """Have the bot join the voice channel of the sender."""
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        if interaction.user.voice is None:
            await interaction.response.send_message(
                "You are not in a voice channel!",
                ephemeral=True
            )
            return

        channel = interaction.user.voice.channel

        if interaction.guild.voice_client is not None:
            await interaction.guild.voice_client.move_to(channel)
        else:
            await channel.connect()

        await interaction.response.send_message(f"Joined {channel.name}")

    @app_commands.command(name="leave", description="Leave the voice channel")
    async def leave(self, interaction: discord.Interaction):
        """Have the bot leave the voice channel."""
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
            await interaction.response.send_message("Disconnected from voice channel.", ephemeral=True)
        else:
            await interaction.response.send_message(
                "I am not in a voice channel.",
                ephemeral=True
            )

    @app_commands.command(name="play", description="Play audio from a YouTube URL")
    @app_commands.describe(url="The YouTube URL")
    async def play(self, interaction: discord.Interaction, url: str):
        """Play audio from a YouTube URL in the sender's voice channel."""
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        if interaction.user.voice is None:
            await interaction.response.send_message(
                "You need to be in a voice channel first.",
                ephemeral=True
            )
            return

        await interaction.response.defer()

        channel = interaction.user.voice.channel

        if interaction.guild.voice_client is None:
            vc = await channel.connect()
        else:
            vc = interaction.guild.voice_client
            if vc.channel != channel:
                await vc.move_to(channel)

        try:
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)

                if "entries" in info:
                    info = info["entries"][0]

                audio_url = info["url"]
                title = info.get("title", "Unknown title")

            if vc.is_playing():
                vc.stop()

            source = discord.FFmpegPCMAudio(
                audio_url,
                executable=FFMPEG_PATH,
                **FFMPEG_OPTIONS
            )

            vc.play(source)
            await interaction.followup.send(f"Now playing: **{title}**")

        except Exception as e:
            await interaction.followup.send(f"Error playing audio: {e}")
            print(f"Play error: {e}")

    @app_commands.command(name="stop", description="Stop playback")
    async def stop(self, interaction: discord.Interaction):
        """Stop the currently playing audio."""
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await interaction.response.send_message("Stopped playback.")
        else:
            await interaction.response.send_message("Nothing is playing.", ephemeral=True)

    @app_commands.command(name="pause", description="Pause playback")
    async def pause(self, interaction: discord.Interaction):
        """Pause the currently playing audio."""
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await interaction.response.send_message("Paused playback.")
        else:
            await interaction.response.send_message("Nothing is playing.", ephemeral=True)

    @app_commands.command(name="resume", description="Resume playback")
    async def resume(self, interaction: discord.Interaction):
        """Resume the currently paused audio."""
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        vc = interaction.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await interaction.response.send_message("Resumed playback.")
        else:
            await interaction.response.send_message("Nothing is paused.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Music(bot))
