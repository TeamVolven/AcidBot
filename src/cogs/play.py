import discord
import shutil
import spotipy

from spotipy.oauth2 import SpotifyClientCredentials
from collections import deque
from discord.ext import commands
from discord import app_commands

queue = deque()  # Queue to store the songs
ffmpeg_path = shutil.which("ffmpeg")

class PlayCMD(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Loaded play.py!")

    @app_commands.command(name="play", description="Plays a song or playlist")
    async def play_command(self, interaction: discord.Interaction, link: str):
        await interaction.response.defer()
        voice_client = discord.utils.get(self.client.voice_clients, guild=interaction.guild)

        channel = interaction.user.voice.channel
        await interaction.followup.send("📡 Connecting to the VC...")
        await channel.connect()
        await interaction.followup.send(content="📞 Connected!!")

        embed = discord.Embed(title="Music Player", color=discord.Color.blue())
        embed.add_field(name="Status", value=f"📡 Attempting to load {link}...")
        await interaction.followup.send(embed=embed)

        try:
            if ffmpeg_path is None:
                raise ValueError("FFmpeg executable not found.")

            if "open.spotify.com/playlist" in link:
                # If the link is a Spotify playlist, retrieve the individual track URLs and add them to the queue
                sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
                playlist_id = link.split('/')[-1]
                playlist = sp.playlist_tracks(playlist_id)
                for item in playlist['items']:
                    track = item['track']
                    artists = ', '.join([artist['name'] for artist in track['artists']])
                    title = f"{artists} - {track['name']}"
                    if 'preview_url' in track and track['preview_url'] is not None:
                        queue.append((title, track['preview_url']))

                if voice_client and not voice_client.is_playing() and not voice_client.is_paused():
                    # If the bot is in a voice channel and no song is currently playing or paused, play the first song from the playlist
                    title, url = queue.popleft()
                    voice_client.play(discord.FFmpegPCMAudio(url))
                    embed.set_field_at(0, name="Status", value=f"🎵 Now playing: {title}")
                    await interaction.followup.send(embed=embed)
                elif voice_client:
                    # If the bot is in a voice channel but a song is already playing or paused, add the songs from the playlist to the queue
                    embed.set_field_at(0, name="Status", value=f"🎵 Added playlist to the queue: {playlist['name']}")
                    await interaction.followup.send(embed=embed)
                else:
                    # If the bot is not in a voice channel, prompt the user to join a voice channel
                    embed.set_field_at(0, name="Status", value="❗ Please join a voice channel first.")
                    await interaction.followup.send(embed=embed)

            elif "open.spotify.com/track" in link:
                # If the link is a Spotify track, add it to the queue
                sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
                track_id = link.split('/')[-1].split('?')[0]
                track = sp.track(track_id)
                artists = ', '.join([artist['name'] for artist in track['artists']])
                title = f"{artists} - {track['name']}"
                if 'preview_url' in track and track['preview_url'] is not None:
                    queue.append((title, track['preview_url']))

                if voice_client and not voice_client.is_playing() and not voice_client.is_paused():
                    # If the bot is in a voice channel and no song is currently playing or paused, play the requested song immediately
                    title, url = queue.popleft()
                    voice_client.play(discord.FFmpegPCMAudio(url))
                    embed.set_field_at(0, name="Status", value=f"🎵 Now playing: {title}")
                    await interaction.edit_original_response(embed=embed)
                elif voice_client:
                    # If the bot is in a voice channel but a song is already playing or paused, add the requested song to the queue
                    embed.set_field_at(0, name="Status", value=f"🎵 Added to the queue: {link}")
                    await interaction.edit_original_response(embed=embed)
                else:
                    # If the bot is not in a voice channel, prompt the user to join a voice channel
                    embed.set_field_at(0, name="Status", value="❗ Please join a voice channel first.")
                    await interaction.edit_original_response(embed=embed)

            else:
                embed.set_field_at(0, name="Status", value=f"❗ The link is not supported.")
                await interaction.edit_original_response(embed=embed)

        except Exception as e:
            embed.set_field_at(0, name="Status", value=f"🛠 Error: {e}")
            print(f"Error: {e}")
            await interaction.edit_original_response(embed=embed)

async def setup(client):
    await client.add_cog(PlayCMD(client))