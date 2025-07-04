import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils.logger import logger
from utils.message_handler import MessageHandler, get_message_handler
from ai_tools.chat_gpt import AIInterpreter
from news_pdf.merge_news import generate_html_report, generate_pdf_report
import asyncio
from config import config
from utils.read_write import read_text_file, write_json_file, write_text_file

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up bot with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Bot is in {len(bot.guilds)} guilds')
    
    # Load command cogs
    await load_cogs()
    
    # Sync slash commands globally using pycord method
    try:
        await bot.sync_commands()
        logger.info("Commands synced successfully!")
        # Print the available slash commands for debugging
        slash_commands = [cmd.name for cmd in bot.application_commands]
        text_commands = [cmd.name for cmd in bot.commands]
        logger.info(f"Available slash commands: {slash_commands}")
        logger.info(f"Available text commands: {text_commands}")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")
    
    # Process and send daily news report
    await process_and_send_news_report() 

async def process_and_send_news_report():
    """
    Complete pipeline to process news messages and send PDF report to Discord.
    Handles: message export → AI processing → PDF generation → Discord sending
    """
    try:
        logger.info("🚀 Starting daily news report processing...")
        
        # Step 1: Export messages from Twitter news channel
        logger.info("📥 Exporting messages from Twitter news channel...")
        message_handler = get_message_handler(bot, 24, [config.user_ids.ifitt_bot])
        output_file_path = await message_handler.export_channel_to_text(config.channel_ids.tweeter_news)
        exported_messages = read_text_file(output_file_path)
        
        if not exported_messages:
            logger.warning("⚠️ No messages exported from Twitter news channel")
            return
        
        # Step 2: Process messages with AI
        logger.info("🤖 Processing messages with AI...")
        ai_interpreter = AIInterpreter()
        news_summary_prompt = read_text_file("ai_tools/prompts/news_to_json_summary_prompt.txt") + exported_messages
        response = ai_interpreter.get_json_response(news_summary_prompt)
        write_json_file("news_pdf/news_data.json", response)
        
        # Step 3: Generate PDF report
        logger.info("📄 Generating PDF report...")
        
        # Determine report time based on current hour
        from datetime import datetime
        current_hour = datetime.now().hour
        report_time = 'morning' if 6 <= current_hour < 18 else 'evening'
        logger.info(f"🌅 Using {report_time} theme (current hour: {current_hour})")
        
        await generate_pdf_report(
            input_json="news_pdf/news_data.json", 
            template_file="news_pdf/template.html", 
            output_file="news_pdf/output.html", 
            pdf_file="news_pdf/output.pdf",
            report_time=report_time
        )
        
        # Step 4: Send report to Discord channel
        logger.info("📤 Sending report to Discord channel...")
        bot_channel = config.channel_ids.python_bot
        channel = bot.get_channel(bot_channel)
        
        if channel:
            try:
                # Send the PDF file
                with open("news_pdf/output.pdf", "rb") as pdf_file:
                    await channel.send(
                        content="📰 **Daily News Report**\nHere's your daily news summary in PDF format:",
                        file=discord.File(pdf_file, filename="daily_news_report.pdf")
                    )
                logger.info("✅ PDF report sent to Discord channel successfully")
            except Exception as e:
                logger.error(f"❌ Failed to send PDF to Discord channel: {e}")
                # Send a fallback message if PDF sending fails
                await channel.send("📰 **Daily News Report**\nNews processing completed, but there was an issue sending the PDF file.")
        else:
            logger.error(f"❌ Could not find channel with ID: {bot_channel}")
            
        logger.info("🎉 Daily news report processing completed!")
        
    except Exception as e:
        logger.error(f"❌ Error in news report processing pipeline: {e}")
        # Try to send error notification to Discord
        try:
            bot_channel = config.channel_ids.python_bot
            channel = bot.get_channel(bot_channel)
            if channel:
                await channel.send(f"❌ **Error in News Processing**\nThere was an error processing the daily news report: {str(e)}")
        except Exception as notify_error:
            logger.error(f"❌ Failed to send error notification: {notify_error}")


async def load_cogs():
    """Load all command cogs"""
    cogs = [
        "cogs.slash.hello",
        "cogs.slash.ping", 
        "cogs.slash.sync",
        "cogs.slash.test",
        "cogs.text.greet",
        "cogs.admin.export"
    ]
    
    loaded_cogs = []
    for cog in cogs:
        try:
            bot.load_extension(cog)
            loaded_cogs.append(cog)
            # logger.info(f"✅ Loaded cog: {cog}")
        except Exception as e:
            logger.error(f"❌ Failed to load cog {cog}: {e}")
    
    logger.info(f"Successfully loaded {len(loaded_cogs)}/{len(cogs)} cogs")
    return loaded_cogs

def main():
    """Main entry point"""
    if not TOKEN:
        raise ValueError("No Discord token found. Please check your .env file.")
    
    try:
        # Use bot.run() instead of asyncio.run() to avoid loop conflicts
        bot.run(TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user (Ctrl+C)")
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        logger.info("Bot shutdown complete")

if __name__ == '__main__':
    main()