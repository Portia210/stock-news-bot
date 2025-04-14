import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from utils.db_manager import DatabaseManager
from utils.logger_config import setup_logger
from utils.ai_interpretation import AIInterpreter


main_logger = setup_logger()

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
TWITTER_CHANNEL_ID = int(os.getenv('TWITTER_CHANNEL_ID'))
BOT_CHANNEL_ID = int(os.getenv('BOT_CHANNEL_ID'))
IFTTT_BOT_ID = int(os.getenv('IFTTT_BOT_ID'))

# Initialize database and AI interpreter
db = DatabaseManager()
ai_interpreter = AIInterpreter(db)

# Set up bot with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    # Sync slash commands with Discord
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="hello", description="Responds with a friendly hello message")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f'Hello {interaction.user.mention}! 👋')

@bot.tree.command(name="ping", description="Check bot's latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f'Pong! Latency: {round(bot.latency * 1000)}ms')


@bot.tree.command(name="read_twitter", description="Reads messages from today from the channel with id TWITTER_CHANNEL_ID")
async def read_twitter(interaction: discord.Interaction, limit: int = 500):
    # Defer the response since this might take a while
    await interaction.response.defer()
    
    try:
        messages_ids = db.get_all_messages_ids()
        channel = bot.get_channel(TWITTER_CHANNEL_ID)
        bot_channel = bot.get_channel(BOT_CHANNEL_ID)
        
        if not channel or not bot_channel:
            await interaction.followup.send("Could not find the Twitter channel or the bot channel. Please check the channel IDs.")
            return

        # Get current time in UTC
        now = datetime.now(timezone.utc)
        today = now.date()
        
        message_count = 0
        new_messages = []
        async for discord_message in channel.history(limit=limit):
            if discord_message.created_at.date() != today:
                break
            
            if str(discord_message.id) in messages_ids:
                continue
                
            if discord_message.author.id != IFTTT_BOT_ID:
                continue
                
            if not discord_message.content:
                continue
            
            message_data = {
                "id": str(discord_message.id),
                "content": discord_message.content,
                "created_at": discord_message.created_at
            }
            new_messages.append(message_data)
            message_count += 1
            
            # Show progress every 100 messages
            if message_count % 100 == 0:
                await interaction.followup.send(f"Processed {message_count} messages so far...")

        await interaction.followup.send(f"Processed {message_count} messages, found {len(new_messages)} new messages")
        
        if new_messages:
            try:
                # Save messages in chronological order (oldest first)
                for message_data in new_messages[::-1]:
                    db.append_message(
                        message_id=message_data["id"],
                        created_at=message_data["created_at"],
                        content=message_data["content"]
                    )
                await interaction.followup.send(f"Successfully saved {len(new_messages)} messages to database")
                
                # Process messages with AI interpreter
                await interaction.followup.send("Starting AI interpretation...")
                ai_interpreter.process_messages(batch_size=10)
                await interaction.followup.send("AI interpretation completed")
                
            except Exception as e:
                await interaction.followup.send(f"Error saving messages to database: {str(e)}")
                
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {str(e)}")

def run_bot():
    if not TOKEN:
        raise ValueError("No Discord token found. Please check your .env file.")
    
    # Initialize database
    db.init_db()
    
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