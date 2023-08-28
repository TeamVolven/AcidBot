import discord
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = discord.Intents.all()
client = commands.Bot(command_prefix='s!', intents=intents)
client.remove_command('help')

Status = discord.Game(name="Music • /help")

@client.event
async def on_ready():
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} commands!")
    except:
        print(f'Already synced')
    print(f"Connected to {client.user}!")
    try:
        await client.change_presence(activity=Status)
    except Exception as e:
        print(f"Error: {e}")

async def setup_cogs():
    for filename in os.listdir('./src/cogs'):
        if filename.endswith('.py'):
            await client.load_extension(f'src.cogs.{filename[:-3]}')

async def main():
    await setup_cogs()
    await client.start(TOKEN)

asyncio.run(main())
    
        
asyncio.run(main())