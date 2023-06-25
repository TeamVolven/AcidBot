import discord,asyncio,shutil
from discord import app_commands
import pytube as pt
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import shutil
from collections import deque
from discord import app_commands, utils
from datetime import timedelta
from discord.ext import commands, tasks
from itertools import cycle

DISCORD_TOKEN = 'import_token_here'

interaction = discord.Interaction
intents = discord.Intents.all()
intents.members = True

client = commands.Bot(command_prefix="s!", intents=intents)

bot_status = cycle([
    "Music"
])

@tasks.loop(seconds=5)
async def change_status():
    await client.change_presence(activity=discord.Streaming(name=next(bot_status), url='https://www.youtube.com/watch?v=dQw4w9WgXcQ'))

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

@client.tree.command(name="help", description="Displays Music Commands...")
async def help_command(interaction):
    embed = discord.Embed(title="Acid Help", description="Displays Music Commands...", color=discord.Color.blue())
    embed.add_field(name="1#: /leave", value="Disconnect from the VC")
    embed.add_feild(name="2#: /play", value="Plays a song or playlist")
    embed.add_feild(name="3#: /stop", value="Stops the currently playing song")
    embed.add_feild(name="4#: /pause", value="Pauses the currently playing song")
    embed.add_feild(name="5#: /resume", value="Resumes the paused song")
    embed.add_feild(name="6#: /skip", value="Skips the current song")
    embed.add_feild(name="7#: /queue", value="Shows the current queue")
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="leave", description="Disconnects from a voice channel")
async def connect_command(interaction):
    try:
        channel = interaction.user.voice.channel
        await interaction.response.send_message("📡 Disconnecting from the VC...")
        await channel.disconnect()
        await interaction.edit_original_response(content=">..Disconnected..<")
    except Exception as e:
        print(f"Error: {e}")
        await interaction.response.send_message("❗ Failed to disconnect from a voice channel.")

queue = deque()  # Queue to store the songs
ffmpeg_path = shutil.which("ffmpeg")

@client.tree.command(name="play", description="Plays a song or playlist")
async def play_command(interaction, link: str):
    await interaction.response.defer()
    voice_client = discord.utils.get(client.voice_clients, guild=interaction.guild)

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

        if "youtube.com/playlist" in link:
            # If the link is a YouTube playlist, retrieve the individual video URLs and add them to the queue
            playlist = pt.Playlist(link)
            for video in playlist.videos:
                t = video.streams.filter(only_audio=True)
                t[0].download()
                queue.append((video.title, t[0].default_filename))

            if voice_client and not voice_client.is_playing() and not voice_client.is_paused():
                # If the bot is in a voice channel and no song is currently playing or paused, play the first song from the playlist
                title, filename = queue.popleft()
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
            # If the link is a single song, add it to the queue
            t = pt.YouTube(link).streams.filter(only_audio=True)
            t[0].download()
            queue.append((link, t[0].default_filename))

            if voice_client and not voice_client.is_playing() and not voice_client.is_paused():
                # If the bot is in a voice channel and no song is currently playing or paused, play the requested song immediately
                title, filename = queue.popleft()
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
    else:
	    await interaction.response.send_message("❗Sorry there is no song playing or I am not in a VC.")

@client.tree.command(name="pause", description="Pauses the currently playing song")
async def pause_command(interaction):
    voice_client = discord.utils.get(client.voice_clients, guild=interaction.guild)
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await interaction.response.send_message("⏸️ Paused the current song.")
    else:
        await interaction.response.send_message("❗Sorry there is no song playing or I am not in a VC.")

@client.tree.command(name="resume", description="Resumes the paused song")
async def resume_command(interaction):
    voice_client = discord.utils.get(client.voice_clients, guild=interaction.guild)
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await interaction.response.send_message("▶️ Resumed the song.")
    else:
        await interaction.response.send_message("❗Sorry there is no song playing or I am not in a VC.")

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
    else:
        await interaction.response.send_message("❗Sorry there is no song to skip or I am not in a VC.")

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
