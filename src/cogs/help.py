import discord
from discord.ext import commands
from discord import app_commands

class HelpCmd(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("Loaded help.py!")

    @app_commands.command(name="help", description="Shows you all of the commands.")
    async def dev_cmd(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Acid Help", description="Displays Music Commands...", color=discord.Color.blue())
        embed.add_field(name="1#: /leave", value="Disconnect from the VC")
        embed.add_feild(name="2#: /play", value="Plays a song or playlist")
        embed.add_feild(name="3#: /stop", value="Stops the currently playing song")
        embed.add_feild(name="4#: /pause", value="Pauses the currently playing song")
        embed.add_feild(name="5#: /resume", value="Resumes the paused song")
        embed.add_feild(name="6#: /skip", value="Skips the current song")
        embed.add_feild(name="7#: /queue", value="Shows the current queue")
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(client):
    await client.add_cog(HelpCmd(client))