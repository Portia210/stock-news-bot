import discord
from discord.ext import commands

class HelloCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @discord.slash_command(name="hello", description="Responds with a friendly hello message")
    async def hello(self, ctx: discord.ApplicationContext):
        await ctx.respond(f'Hello {ctx.user.mention}! 👋')

def setup(bot):
    bot.add_cog(HelloCommands(bot)) 