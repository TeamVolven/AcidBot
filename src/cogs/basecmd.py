import discord
import shutil
import spotipy

from spotipy.oauth2 import SpotifyClientCredentials
from collections import deque
from discord.ext import commands
from discord import app_commands

queue = deque()  # Queue to store the songs
ffmpeg_path = shutil.which("ffmpeg")

class BaseCMDs(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Loaded basecmd.py!")

    @app_commands.command(name="leave", description="Disconnects from a voice channel")
    async def connect_command(self, interaction: discord.Interaction):
        try:
            channel = interaction.user.voice.channel
            await interaction.response.send_message("📡 Disconnecting from the VC...")
            await channel.disconnect()
            await interaction.edit_original_response(content=">..Disconnected..<")
        except Exception as e:
            print(f"Error: {e}")
            await interaction.response.send_message("❗ Failed to disconnect from a voice channel.")

    @app_commands.command(name="stop", description="Stops the currently playing song")
    async def stop_command(self, interaction: discord.Interaction):
        voice_client = discord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await interaction.response.send_message("⏹️ Stopped the current song.")
            queue.clear()  # Clear the queue when stopping the song
        else:
            await interaction.response.send_message("❗Sorry there is no song playing or I am not in a VC.")

    @app_commands.command(name="pause", description="Pauses the currently playing song")
    async def pause_command(self, interaction: discord.Interaction):
        voice_client = discord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await interaction.response.send_message("⏸️ Paused the current song.")
        else:
            await interaction.response.send_message("❗Sorry there is no song playing or I am not in a VC.")

    @app_commands.command(name="resume", description="Resumes the paused song")
    async def resume_command(self, interaction: discord.Interaction):
        voice_client = discord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await interaction.response.send_message("▶️ Resumed the song.")
        else:
            await interaction.response.send_message("❗Sorry there is no song playing or I am not in a VC.")

    @app_commands.command(name="skip", description="Skips the current song")
    async def skip_command(self, interaction: discord.Interaction):
        voice_client = discord.utils.get(self.client.voice_clients, guild=interaction.guild)
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await interaction.response.send_message("⏭️ Skipped the current song.")
            if queue:
                # If there are songs in the queue, play the next song
                title, source = queue.pop(0)
                if "youtube.com" in source:
                    voice_client.play(discord.FFmpegPCMAudio(executable=ffmpeg_path, source=source))
                elif "spotify.com" in source:
                    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
                    track = sp.track(source)
                    if 'preview_url' in track and track['preview_url'] is not None:
                        voice_client.play(discord.FFmpegPCMAudio(track['preview_url']))
                embed = discord.Embed(title="Music Player", color=discord.Color.blue())
                embed.add_field(name="Status", value=f"🎵 Now playing: {title}")
                embed.set_footer(text="Developed by: WaterMeloDev", icon_url="https://cdn.discordapp.com/avatars/1119006375868104805/c72540b3fbb57b01ed126b0c58933688.png?size=4096")
                await interaction.followup.send(embed=embed)
        else:
            await interaction.response.send_message("❗Sorry there is no song to skip or I am not in a VC.")

    @app_commands.command(name="queue", description="Shows the current queue")
    async def queue_command(self, interaction: discord.Interaction):
        if queue:
            embed = discord.Embed(title="Music Player - Queue", color=discord.Color.blue())
            for i, (title, _) in enumerate(queue, start=1):
                embed.add_field(name=f"#{i}", value=title, inline=False)
            
            embed.set_footer(text="Developed by: WaterMeloDev", icon_url="https://cdn.discordapp.com/avatars/1119006375868104805/c72540b3fbb57b01ed126b0c58933688.png?size=4096")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("📭 The queue is empty.")

async def setup(client):
    await client.add_cog(BaseCMDs(client))