import discord
from discord.ext import commands

class TestCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @discord.slash_command(name="test", description="Simple test command")
    async def test(self, ctx: discord.ApplicationContext):
        await ctx.respond("Test command works! ✅")

def setup(bot):
    bot.add_cog(TestCommands(bot)) 