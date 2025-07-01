import discord
from datetime import datetime, timezone, timedelta
from utils.logger_config import logger
import os

class MessageHandler:
    def __init__(self, bot):
        self.bot = bot
        self.data_dir = "data"
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """Ensure the data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logger.info(f"Created data directory: {self.data_dir}")
    
    async def export_channel_to_text(self, channel_id: int, hours_back: int = 24):
        """
        Read messages from a channel and save to a text file
        
        Args:
            channel_id (int): Discord channel ID
            hours_back (int): Number of hours to look back (default: 24)
        
        Returns:
            str: Path to the saved file, or None if failed
        """
        try:
            channel = self.bot.get_channel(channel_id)
            if not channel:
                logger.error(f"Channel {channel_id} not found")
                return None
            
            # Calculate the time threshold
            threshold_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{channel.name}_{timestamp}.txt"
            filepath = os.path.join(self.data_dir, filename)
            
            # Read messages and write to file
            message_count = 0
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Channel: {channel.name}\n")
                f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Messages from last {hours_back} hours\n")
                f.write("=" * 50 + "\n\n")
                
                async for message in channel.history(limit=None, after=threshold_time):
                    timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
                    author = message.author.display_name
                    content = message.content.replace('\n', ' ').strip()
                    
                    if content:  # Only write messages with content
                        f.write(f"[{timestamp}] {author}: {content}\n")
                        message_count += 1
            
            logger.info(f"Exported {message_count} messages from {channel.name} to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting channel {channel_id}: {e}")
            return None

# Global message handler instance
message_handler = None

def get_message_handler(bot):
    """Get or create the global message handler instance"""
    global message_handler
    if message_handler is None:
        message_handler = MessageHandler(bot)
    return message_handler 