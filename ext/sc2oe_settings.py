from discord.ext import commands
import logging
import os
import toml

from .utils import permissions as perms


log = logging.getLogger(__name__)


class SC2OESettings():
    def __init__(self, bot):
        self.bot = bot
        self.DATA_PATH = './data/sc2oe/'
        self.INFO_FILE = 'srvInf.toml'
        if os.path.isdir(self.DATA_PATH) is False:
            os.makedirs(self.DATA_PATH)
        if os.path.isfile(self.DATA_PATH + self.INFO_FILE) is False:
            open(self.DATA_PATH+self.INFO_FILE, 'a').close()
        self.srvInf = toml.load(self.DATA_PATH + self.INFO_FILE)

    @commands.group(name='set')
    async def _settings(self, ctx):
        """ Change a setting """
        if perms._check(ctx, 3):
            pass
        else:
            await ctx.send('You have no permissions to execute this command.')

    @_settings.command(name='channel')
    async def _settings_channel(self, ctx, *, t: str):
        """ Change the channel, the bot posts events in """
        s = t.split(' ')
        if len(s) == 2 and s[0].lower() in ['general', 'amateur', 'team']:
            self.srvInf['guilds'][ctx.guild.name][f'channel_{s[0].lower()}'] = s[1].lower()
            f = open(self.DATA_PATH+self.INFO_FILE, 'w')
            toml.dump(self.srvInf, f)
            f.close()
            await ctx.channel.send(f'Changed the {s[0].lower()} events channel to {s[1].lower()}')
        else:
            await ctx.channel.send('Error: only 2 arguments allowed.\n Arg 1: channel type (General, Amateur, Team) \nArg 2: channel-name')

    @_settings.command(name='time')
    async def _settings_time(self, ctx, *, t: int):
        """ Set the timeformat (24h- or 12ham/pm-format) """
        if len(t) == 1:
            if t in [12, 24]:
                self.srvInf['guilds'][ctx.guild.name]['timeformat'] = t
                f = open(self.DATA_PATH+self.INFO_FILE, 'w')
                toml.dump(self.srvInf, f)
                f.close()
                await ctx.channel.send(f'Changed the time format to {t} hours')
            else:
                await ctx.channel.send('Error: time has to be either `12` or `24` hour format')


    @commands.command(name='permcheck')
    async def _check_permissions(self, ctx):
        lvl = [0]
        pname = ''
        if perms._check(ctx, 5):
            lvl.append(5)
            pname = 'Phoenix'
        elif perms._check(ctx, 4):
            lvl.append(4)
            pname = 'Server Owner'
        elif perms._check(ctx, 3):
            lvl.append(3)
            pname = 'Admin'
        elif perms._check(ctx, 2):
            lvl.append(2)
            pname = 'Moderator'
        elif perms._check(ctx, 1):
            lvl.append(1)
            pname = 'User'
        else:
            pname = 'Bot'
        await ctx.channel.send(f'Your permission level is {max(lvl)} - ({pname}).')



def setup(bot):
    n = SC2OESettings(bot)
    bot.add_cog(n)
