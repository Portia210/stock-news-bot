import discord
from datetime import datetime, timezone, timedelta
from utils.logger import logger
import os

class MessageHandler:
    def __init__(self, bot, hours_back: int = 24, user_ids: list = None):
        self.bot = bot
        self.hours_back = hours_back
        self.user_ids = user_ids
        self._validate_user_ids()
        self._setup_directories()
    

    def _validate_user_ids(self):
        """Check if the user IDs are valid"""
        if self.user_ids:
            for user_id in self.user_ids:
                if not self.bot.get_user(user_id):
                    logger.error(f"User ID {user_id} is not valid")
                    self.user_ids.remove(user_id)


    def _setup_directories(self):
        """Initialize and setup required directories"""
        self.data_dir = os.path.join("data", "messages export")
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logger.info(f"Created data directory: {self.data_dir}")
    
    def _get_timestamp(self):
        """Get current timestamp in milliseconds"""
        return int(datetime.now().timestamp() * 1000)
    
    def _get_user_names(self) -> list:
        return [self.bot.get_user(user_id).name for user_id in self.user_ids] if self.user_ids else []

    def _format_filename(self, channel_name: str) -> str:
        """Generate filename for export"""
        timestamp = self._get_timestamp()
        filename = f"{channel_name}_last_{self.hours_back}_hours"
        
        if self.user_ids:
            filename += f"_filtered_{len(self.user_ids)}users"
        
        filename += f"_{timestamp}.txt"
        return filename
    
    async def read_channel_messages(self, channel_id: int):
        """
        Read messages from a channel using class variables
        
        Args:
            channel_id (int): Discord channel ID
        
        Returns:
            tuple: (messages_list, channel_name, message_count) or (None, None, 0) if failed
        """
        try:
            channel = self.bot.get_channel(channel_id)
            
            # Calculate the time threshold
            threshold_time = datetime.now(timezone.utc) - timedelta(hours=self.hours_back)
            
            # Read messages
            messages_list = []
            
            async for message in channel.history(limit=None, after=threshold_time):
                # Filter by user if user_ids is provided
                if self.user_ids and message.author.id not in self.user_ids:
                    continue
                    
                timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
                author = message.author.display_name
                content = message.content.replace('\n', ' ').strip()
                
                if content:  # Only include messages with content
                    messages_list.append({
                        'timestamp': timestamp,
                        'author': author,
                        'content': content
                    })
            
            logger.info(f"Read {len(messages_list)} messages from {channel.name}")
            return messages_list, channel.name
            
        except Exception as e:
            logger.error(f"Error reading channel {channel_id}: {e}")
            return None, None, 0

    async def save_messages_to_file(self, messages_list: list, channel_name: str):
        """
        Save messages to a text file using class variables
        
        Args:
            messages_list (list): List of message dictionaries
            channel_name (str): Name of the channel
        
        Returns:
            str: Path to the saved file, or None if failed
        """
        try:
            filename = self._format_filename(channel_name)
            filepath = os.path.join(self.data_dir, filename)
            
            user_names = ", ".join(self._get_user_names()) if self.user_ids else "all users"
            # Write messages to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Channel: {channel_name}\n")
                f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Messages from last {self.hours_back} hours\n")
                f.write(f"Wrote by: {user_names}\n")
                f.write("=" * 50 + "\n\n")
                
                for message in messages_list:
                    f.write(f"[{message['timestamp']}] {message['author']}: {message['content']}\n")
            
            logger.info(f"Saved {len(messages_list)} messages to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving messages to file: {e}")
            return None

    async def export_channel_to_text(self, channel_id: int):
        """
        Read messages from a channel and save to a text file
        
        Args:
            channel_id (int): Discord channel ID
        
        Returns:
            str: Path to the saved file, or None if failed
        """
        # Read messages
        messages_list, channel_name = await self.read_channel_messages(channel_id)
        
        if messages_list is None:
            return None
        
        # Save messages to file
        filepath = await self.save_messages_to_file(messages_list, channel_name)
        
        return filepath

# Global message handler instance
message_handler = None

def get_message_handler(bot, hours_back: int = 24, user_ids: list = None):
    """Get or create the global message handler instance"""
    global message_handler
    if message_handler is None:
        message_handler = MessageHandler(bot, hours_back, user_ids)
    return message_handler 