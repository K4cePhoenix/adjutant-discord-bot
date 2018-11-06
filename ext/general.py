from datetime import datetime
from discord.ext import commands
import discord
import logging
import platform
import pytz
import time

from .utils import permissions as perms


log = logging.getLogger('adjutant.general')


class General():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping')
    async def _ping(self, ctx):
        """ Check the bot latency. """
        pingtime = time.time()
        embed = discord.Embed(title="Pinging...", colour=0xFF0000)
        msg = await ctx.send(embed=embed)
        ping = time.time() - pingtime
        em = discord.Embed(title='Pong!', description=f'Response latency: {1000.*ping:.2f}ms\nWebSocket latency: {1000.*self.bot.latency:.2f}ms', colour=0x00FF00)
        await msg.edit(embed=em)

    @commands.command(name="help")
    async def _help(self, ctx):
        """ Displays a list of Adjutants commands. """
        embed = discord.Embed(color=discord.Colour.blue(), title="Adjutant DiscordBot", description="My prefices are `a>` and `a!`.")
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.set_footer(text="By Phoenix#2694", icon_url="https://avatars2.githubusercontent.com/u/36424912?s=60&v=4")
        embed.add_field(name="Commands", value="See a list of all commands [here](https://k4cephoenix.github.io/#commands).", inline=False)
        embed.add_field(name="Invite", value=f"Invite Adjutant to your server [here](https://discordapp.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot&permissions=85056).", inline=False)
        embed.add_field(name="Server", value="Join Adjutants support server [here](https://discordapp.com/invite/nfa9jnu).", inline=False)
        embed.add_field(name="More Information", value="You can find more information using the `info` command.", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='info')
    async def _info(self, ctx):
        """ Display information about Adjutant. """
        users = sum(1 for _ in self.bot.get_all_members())
        embed = discord.Embed(color=discord.Colour.blue(), title="Adjutant Information", description="")
        embed.set_footer(text="By Phoenix#2694", icon_url="https://avatars2.githubusercontent.com/u/36424912?s=60&v=4")
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        try:
            embed.add_field(name="Statistics: ", value=f"Servers: **{len(self.bot.guilds)}**\nShards: **{len(self.bot.shards)}**\nUsers: **{users}**\nUptime: **{str(datetime.now(tz=pytz.utc)-self.bot.START_TIME).split('.')[0]}**")
        except:
            embed.add_field(name="Statistics: ", value=f"Servers: **{len(self.bot.guilds)}**\nUsers: **{users}**\nUptime: **{str(datetime.now(tz=pytz.utc)-self.bot.START_TIME).split('.')[0]}**")
        embed.add_field(name="Version: ", value=f"Adjutant: **{self.bot.VERSION}**\ndiscord.py: **{discord.__version__}**\nPython: **{platform.python_version()}**")
        embed.add_field(name="Other: ", value="Website: https://k4cephoenix.github.io/\nDiscord: https://discord.gg/nfa9jnu")
        await ctx.send(embed=embed)

    @commands.command(name='user')
    async def _user(self, ctx):
        """ Shows info on the specified user. """
        user = ctx.message.author
        roles = []
        for r in user.roles:
            if "everyone" not in r.name:
                roles.append(r.name)
        userRoles = "\n".join(roles)
        embed = discord.Embed(color=user.color, description=f"Here's some information about {user.name}!")
        if perms._check(ctx, 5):
            embed.title = f"{user} 🐦"
        elif perms._check(ctx, 4):
            embed.title = f"{user} 🦆"
        elif perms._check(ctx, 3):
            embed.title = f"{user} 🐧"
        elif perms._check(ctx, 2):
            embed.title = f"{user} 🐔"
        elif perms._check(ctx, 1):
            embed.title = f"{user} 🐣"
        else:
            embed.title = f"{user}"
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name="Username", value=user.name, inline=False)
        embed.add_field(name="Discriminator", value=user.discriminator, inline=False)
        embed.add_field(name="ID", value=str(user.id), inline=False)
        if len(user.roles) > 1:
            embed.add_field(name="Roles", value=userRoles, inline=False)
        embed.add_field(name="Date of Account Creation", value=user.created_at.strftime('%Y/%m/%d'), inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='server')
    async def _server(self, ctx):
        """Link to the Adjutant support guild. """
        embed = discord.Embed(title="Join my guild!", description="You can join my guild [here](https://discord.gg/nfa9jnu).")
        await ctx.send(embed=embed)

    @commands.command(name='invite')
    async def _invite(self, ctx):
        """ Link to add Adjutant to a guild. """
        embed = discord.Embed(title="Invite me!", description=f"You can invite me [here](https://discordapp.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot&permissions=85056).")
        await ctx.send(embed=embed)


def setup(bot):
    n = General(bot)
    bot.add_cog(n)
