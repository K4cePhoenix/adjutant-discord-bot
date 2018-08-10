from contextlib import redirect_stdout
import discord
from discord.ext import commands
import io
import subprocess
import textwrap
import traceback

from .utils import permissions as perms

class Administration:
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])
        return content.strip('` \n')

    @commands.command(name='eval')
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""

        if perms._check(ctx, 5): # meh
            env = {
                'bot': self.bot,
                'ctx': ctx,
                'channel': ctx.channel,
                'author': ctx.author,
                'guild': ctx.guild,
                'message': ctx.message,
                '_': self._last_result
            }
            env.update(globals())

            body = self.cleanup_code(body)
            stdout = io.StringIO()

            to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

            try:
                exec(to_compile, env)
            except Exception as e:
                return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

            func = env['func']
            try:
                with redirect_stdout(stdout):
                    ret = await func()
            except Exception as e:
                value = stdout.getvalue()
                await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
            else:
                value = stdout.getvalue()
                try:
                    await ctx.message.add_reaction('☑')
                except:
                    pass

                if ret is None:
                    if value:
                        await ctx.send(f'```py\n{value}\n```')
                else:
                    self._last_result = ret
                    await ctx.send(f'```py\n{value}{ret}\n```')

    @commands.command()
    async def load(self, ctx, *, module):
        """Loads a module."""
        if perms._check(ctx, 4): # Ducklings and meh
            try:
                self.bot.load_extension(module)
            except Exception as e:
                await ctx.send(f'```py\n{traceback.format_exc()}\n```')
            else:
                try:
                    await ctx.message.add_reaction('☑')
                except:
                    pass

    @commands.command()
    async def unload(self, ctx, *, module):
        """Unloads a module."""
        if perms._check(ctx, 4): # Ducklings and meh
            try:
                self.bot.unload_extension(module)
            except Exception as e:
                await ctx.send(f'```py\n{traceback.format_exc()}\n```')
            else:
                try:
                    await ctx.message.add_reaction('☑')
                except:
                    pass

    @commands.command()
    async def reload(self, ctx, *, module):
        """Reloads a module."""
        if perms._check(ctx, 4): # Ducklings and meh
            try:
                self.bot.unload_extension(module)
                self.bot.load_extension(module)
            except Exception as e:
                await ctx.send(f'```py\n{traceback.format_exc()}\n```')
            else:
                try:
                    await ctx.message.add_reaction('☑')
                except:
                    pass

def setup(bot):
    n = Administration(bot)
    bot.add_cog(n)