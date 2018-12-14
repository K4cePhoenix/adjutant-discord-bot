from discord.ext import commands
import logging
import traceback

from .utils import permissions as perms


log = logging.getLogger('adjutant.admin')


class Administration:
    def __init__(self, bot):
        self.bot = bot
        self._lastResult = None

    @commands.command(name='load')
    async def _load(self, ctx, *, module):
        """Loads a module."""
        if perms._check(ctx, 4):
            try:
                self.bot.load_extension('ext.'+module)
            except Exception as e:
                await ctx.send(f'```py\n{e.__class__.__name__}:\n{traceback.format_exc()}\n```')
            else:
                try:
                    await ctx.message.add_reaction('☑')
                except Exception as e:
                    await ctx.send(f'```py\n{e.__class__.__name__}:\n{traceback.format_exc()}\n```')
        else:
            try:
                await ctx.message.add_reaction('❌')
            except Exception as e:
                await ctx.send(f'```py\n{e.__class__.__name__}:\n{traceback.format_exc()}\n```')

    @commands.command(name='unload')
    async def _unload(self, ctx, *, module):
        """Unloads a module."""
        if perms._check(ctx, 4):
            try:
                self.bot.unload_extension('ext.'+module)
            except Exception as e:
                await ctx.send(f'```py\n{e.__class__.__name__}:\n{traceback.format_exc()}\n```')
            else:
                try:
                    await ctx.message.add_reaction('☑')
                except Exception as e:
                    await ctx.send(f'```py\n{e.__class__.__name__}:\n{traceback.format_exc()}\n```')
        else:
            try:
                await ctx.message.add_reaction('❌')
            except Exception as e:
                await ctx.send(f'```py\n{e.__class__.__name__}:\n{traceback.format_exc()}\n```')

    @commands.command(name='reload')
    async def _reload(self, ctx, *, module):
        """Reloads a module."""
        if perms._check(ctx, 4):
            try:
                self.bot.unload_extension('ext.'+module)
                self.bot.load_extension('ext.'+module)
            except Exception as e:
                await ctx.send(f'```py\n{e.__class__.__name__}:\n{traceback.format_exc()}\n```')
            else:
                try:
                    await ctx.message.add_reaction('☑')
                except Exception as e:
                    await ctx.send(f'```py\n{e.__class__.__name__}:\n{traceback.format_exc()}\n```')
        else:
            try:
                await ctx.message.add_reaction('❌')
            except Exception as e:
                await ctx.send(f'```py\n{e.__class__.__name__}:\n{traceback.format_exc()}\n```')


def setup(bot):
    n = Administration(bot)
    bot.add_cog(n)
    