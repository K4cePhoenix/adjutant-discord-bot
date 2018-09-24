from discord.ext import commands
import logging
import toml


log = logging.getLogger('adjutant.patreon')


class Patreon():
    def __init__(self, bot):
        self.bot = bot
        self.PATREON_FILE_PATH = './data/patreon/patreon.toml'
        self.sc2patreons = toml.load(self.PATREON_FILE_PATH)

    @commands.command(name='patreons')
    async def _patreons(self, ctx):
        """ Sends a link to the SC2 Patreons spreadsheet. """
        await ctx.send("You can find a list of Patreons related to SC2 projects & persona, thanks to @TrangLe92 and contributors.\nhttps://docs.google.com/spreadsheets/d/1qJFAw-uOquuwW9_JYbIDFZlL3RrVifIAn8tOgW3H0gA")


def setup(bot):
    n = Patreon(bot)
    bot.add_cog(n)