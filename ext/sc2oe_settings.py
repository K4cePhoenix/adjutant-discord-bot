from discord.ext import commands
import asyncio
import discord
import logging
import os
import toml

from .utils import permissions as perms


log = logging.getLogger(__name__)


class SC2OESettings():
    def __init__(self, adjutant):
        self.adjutant = adjutant
        self.data_path = './data/sc2oe/'
        self.info_file = 'srvInf.toml'
        if os.path.isdir(self.data_path) is False:
            os.makedirs(self.data_path)
        if os.path.isfile(self.data_path + self.info_file) is False:
            open(self.data_path+self.info_file, 'a').close()
        self.srvInf = toml.load(self.data_path + self.info_file)

    @commands.group(name='set')
    async def _settings(self, ctx):
        """ Change a setting """
        if perms._check(ctx, 3):
            pass
        else:
            print('You have no permissions to execute this command.')

    @_settings.command(name='channel')
    async def settings_channel(self, ctx, *, t: str):
        s = t.split(' ')
        if len(s) == 2:
            self.srvInf['guilds'][ctx.guild.name]['channel_{}'.format(s[0])] = s[1]
            f = open(self.data_path+self.info_file, 'w')
            toml.dump(self.srvInf, f)
            f.close()
            await ctx.channel.send('Changed the {} events channel to {}'.format(s[0], s[1]))
        else:
            await ctx.channel.send('Error: only 2 arguments allowed.\n Arg 1: channel type (gnrl, amtr, team) \nArg 2: channel-name')

    @_settings.command(name='time')
    async def settings_time(self, ctx, *, t: int):
        if len(t) == 1:
            if t in [12, 24]:
                self.srvInf['guilds'][ctx.guild.name]['timeformat'] = t
                f = open(self.data_path+self.info_file, 'w')
                toml.dump(self.srvInf, f)
                f.close()
                await ctx.channel.send('Changed the time format to {} hours'.format(t))
            else:
                await ctx.channel.send('Error: time has to be either `12` or `24` hour format')


def setup(adjutant):
    n = SC2OESettings(adjutant)
    adjutant.add_cog(n)
