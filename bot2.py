import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from utils.logger import setup_logger
from config import config


main_logger = setup_logger()

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')



# Set up bot with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    # send hello message to channel
    channel = bot.get_channel(config.channel_ids.python_bot)
    admin_user = bot.get_user(config.user_ids.admin)
    await channel.send(f'bot is ready! {admin_user.mention}!\nAvailable commands: {[cmd.name for cmd in bot.application_commands]}')
    
    # Sync slash commands with Discord
    # try:
    #     await bot.sync_commands()
    #     print("Commands synced successfully!")
    # except Exception as e:
    #     print(f"Failed to sync commands: {e}")
    
    # print the available commands
    print(f'Available commands: {[cmd.name for cmd in bot.application_commands]}')
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')


@bot.slash_command(name="hello", description="Responds with a friendly hello message")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond(f'Hello {ctx.user.mention}! 👋')

@bot.slash_command(name="ping", description="Check bot's latency")
async def ping(ctx: discord.ApplicationContext):
    await ctx.respond(f'Pong! Latency: {round(bot.latency * 1000)}ms')

@bot.slash_command(name="test", description="Test command")
async def test(ctx: discord.ApplicationContext):
    await ctx.respond(f'test command')


# @bot.slash_command(name="noise", description="Make noise")
# async def make_noise(ctx: discord.ApplicationContext):
#     await ctx.respond(f'noise')

@bot.command(name="regular", description="Regular command")
async def regular(ctx):
    await ctx.send(f'regular command')

@bot.slash_command(name="sync", description="Manually sync slash commands")
async def sync_commands(ctx: discord.ApplicationContext):
    try:
        await bot.sync_commands()
        await ctx.respond("Commands synced successfully!", ephemeral=True)
    except Exception as e:
        await ctx.respond(f"Failed to sync commands: {e}", ephemeral=True)

def run_bot():
    if not TOKEN:
        raise ValueError("No Discord token found. Please check your .env file.")
    
    try:
        bot.run(TOKEN)
    except KeyboardInterrupt:
        print("Bot shutdown requested...")
    except Exception as e:
        print(f"Bot error: {e}")
    finally:
        # Cleanup if needed
        pass

# Run the bot
if __name__ == '__main__':
    run_bot()