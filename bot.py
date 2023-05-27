import discord, sqlite3, datetime, math, asyncio, requests, aiohttp, random, json, pytz, os, dotenv, shutil
from discord import app_commands
import pytube as pt
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from discord import app_commands, utils
from datetime import timedelta
from discord.ext import commands, tasks
from itertools import cycle
# from discord.ui import Button, View

dotenv.load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

interaction = discord.Interaction
intents = discord.Intents.all()
intents.members = True

client = commands.Bot(command_prefix="s!", intents=intents)

bot_status = cycle([
    "Programmed by: BoostieDev#5662"
])

@tasks.loop(seconds=5)
async def change_status():
    await client.change_presence(activity=discord.Game(next(bot_status)))

client.remove_command('help')


@client.event
async def on_ready():
        try: 
            synced = await client.tree.sync()
            print(f"Synced {len(synced)} commands!")
        except:
            print('already synced')

        change_status.start()
        print(f"Sucessfully logged in as {client.user}")

@client.tree.command(name = "connect", description = "connects to vc")
async def first_command(interaction):
    # Connects to the music VC on ID...
    await interaction.response.send_message("📡 Connecting to the Music VC...")
    voice_channel = client.get_channel(1111860931295715338) # replace ID with the Local Server Mucic ID VC
    await voice_channel.connect() # VC connect.
    try:
        await interaction.edit_original_response(content="📞 Connected!!")
    except Exception as e:
        print(f"Error: {e}")


queue = []  # Queue to store the songs
ffmpeg_path = shutil.which("ffmpeg")

@client.tree.command(name="play", description="Plays a song or playlist")
async def play_command(interaction, link: str):
    embed = discord.Embed(title="Music Player", color=discord.Color.blue())
    embed.add_field(name="Status", value=f"📡 Attempting to load {link}...")
    await interaction.response.send_message(embed=embed)

    try:
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path is None:
            raise ValueError("FFmpeg executable not found.")
        
        voice_client = discord.utils.get(client.voice_clients, guild=interaction.guild)
        
        if "youtube.com/playlist" in link:
            # If the link is a YouTube playlist, retrieve the individual video URLs and add them to the queue
            playlist = pt.Playlist(link)
            for video in playlist.videos:
                t = video.streams.filter(only_audio=True)
                t[0].download()
                queue.append((video.title, t[0].default_filename))
            
            if voice_client and (not voice_client.is_playing() and not voice_client.is_paused()):
                # If the bot is in a voice channel and no song is currently playing or paused, play the first song from the playlist
                title, filename = queue.pop(0)
                voice_client.play(discord.FFmpegPCMAudio(executable=ffmpeg_path, source=filename))
                embed.set_field_at(0, name="Status", value=f"🎵 Now playing: {title}")
                await interaction.edit_original_response(embed=embed)
            elif voice_client:
                # If the bot is in a voice channel but a song is already playing or paused, add the songs from the playlist to the queue
                embed.set_field_at(0, name="Status", value=f"🎵 Added playlist to the queue: {playlist.title}")
                await interaction.edit_original_response(embed=embed)
            else:
                # If the bot is not in a voice channel, prompt the user to join a voice channel
                embed.set_field_at(0, name="Status", value="❗ Please join a voice channel first.")
                await interaction.edit_original_response(embed=embed)
        
        elif "open.spotify.com/playlist" in link:
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
            
            if voice_client and (not voice_client.is_playing() and not voice_client.is_paused()):
                # If the bot is in a voice channel and no song is currently playing or paused, play the first song from the playlist
                title, url = queue.pop(0)
                voice_client.play(discord.FFmpegPCMAudio(url))
                embed.set_field_at(0, name="Status", value=f"🎵 Now playing: {title}")
                await interaction.edit_original_response(embed=embed)
            elif voice_client:
                # If the bot is in a voice channel but a song is already playing or paused, add the songs from the playlist to the queue
                embed.set_field_at(0, name="Status", value=f"🎵 Added playlist to the queue: {playlist['name']}")
                await interaction.edit_original_response(embed=embed)
            else:
                # If the bot is not in a voice channel, prompt the user to join a voice channel
                embed.set_field_at(0, name="Status", value="❗ Please join a voice channel first.")
                await interaction.edit_original_response(embed=embed)
        
        else:
            # If the link is a single song, add it to the queue
            t = pt.YouTube(link).streams.filter(only_audio=True) 
            t[0].download()
            queue.append((link, t[0].default_filename))
            
            if voice_client and (not voice_client.is_playing() and not voice_client.is_paused()):
                # If the bot is in a voice channel and no song is currently playing or paused, play the requested song immediately
                title, filename = queue.pop(0)
                voice_client.play(discord.FFmpegPCMAudio(executable=ffmpeg_path, source=filename))
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
        
    except Exception as e:
        embed.set_field_at(0, name="Status", value=f"🛠 Error: {e}")
        print(f"Error: {e}")
        await interaction.edit_original_response(embed=embed)

@client.tree.command(name="stop", description="Stops the currently playing song")
async def stop_command(interaction):
    voice_client = discord.utils.get(client.voice_clients, guild=interaction.guild)
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await interaction.response.send_message("⏹️ Stopped the current song.")
        queue.clear()  # Clear the queue when stopping the song

@client.tree.command(name="pause", description="Pauses the currently playing song")
async def pause_command(interaction):
    voice_client = discord.utils.get(client.voice_clients, guild=interaction.guild)
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await interaction.response.send_message("⏸️ Paused the current song.")

@client.tree.command(name="resume", description="Resumes the paused song")
async def resume_command(interaction):
    voice_client = discord.utils.get(client.voice_clients, guild=interaction.guild)
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await interaction.response.send_message("▶️ Resumed the song.")

@client.tree.command(name="skip", description="Skips the current song")
async def skip_command(interaction):
    voice_client = discord.utils.get(client.voice_clients, guild=interaction.guild)
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
            await interaction.followup.send(embed=embed)

@client.tree.command(name="queue", description="Shows the current queue")
async def queue_command(interaction):
    if queue:
        embed = discord.Embed(title="Music Player - Queue", color=discord.Color.blue())
        for i, (title, _) in enumerate(queue, start=1):
            embed.add_field(name=f"#{i}", value=title, inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("📭 The queue is empty.")


async def main():
    async with client:
        await client.start(DISCORD_TOKEN)
    
        
asyncio.run(main())