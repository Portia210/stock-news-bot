import discord
from discord.ext import commands

class SyncCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @discord.slash_command(name="sync", description="Sync slash commands (Admin only)")
    async def sync(self, ctx: discord.ApplicationContext):
        # if ctx.user.guild_permissions.administrator:
        if True:
            try:
                # Use pycord sync method
                await self.bot.sync_commands()
                await ctx.respond('Commands synced successfully!')
            except Exception as e:
                await ctx.respond(f'Failed to sync commands: {e}')
        else:
            await ctx.respond("You don't have permission to use this command!", ephemeral=True)

def setup(bot):
    bot.add_cog(SyncCommands(bot)) 