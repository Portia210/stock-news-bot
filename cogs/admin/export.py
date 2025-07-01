import discord
from discord.ext import commands
from utils.logger_config import logger
from utils.message_handler import get_message_handler

class ExportCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @discord.slash_command(name="export", description="Export messages from a channel to text file (Admin only)")
    async def export_messages(self, ctx: discord.ApplicationContext, channel: discord.TextChannel, hours: int = 24):
        """
        Export messages from a channel to a text file
        
        Args:
            channel: The channel to export messages from
            hours: Number of hours to look back (default: 24)
        """
        if not ctx.user.guild_permissions.administrator:
            await ctx.respond("You need administrator permissions to use this command!", ephemeral=True)
            return
        
        await ctx.defer()
        
        try:
            message_handler = get_message_handler(self.bot)
            filepath = await message_handler.export_channel_to_text(channel.id, hours)
            
            if filepath:
                await ctx.followup.send(f"✅ Successfully exported {channel.mention} messages to: `{filepath}`")
            else:
                await ctx.followup.send(f"❌ Failed to export messages from {channel.mention}")
                
        except Exception as e:
            logger.error(f"Error in export command: {e}")
            await ctx.followup.send(f"❌ Error exporting messages: {str(e)}")

def setup(bot):
    bot.add_cog(ExportCommands(bot)) 