from discord.ext import commands
import aiofiles
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

    async def _save_serverinfo_file(self, evType, g, t):
        self.srvInf['guilds'][g][f'channel_{evType}'] = t.lower()
        tomlStr = toml.dumps(self.srvInf)
        async with aiofiles.open(self.DATA_PATH+self.INFO_FILE, mode='w') as f:
            await f.write(tomlStr)


    @commands.group(name='set')
    async def _settings(self, ctx):
        """ Change a setting """
        if perms._check(ctx, 3):
            # self.srvInf = toml.load(self.DATA_PATH + self.INFO_FILE)
            async with aiofiles.open(self.DATA_PATH+self.INFO_FILE, mode='r') as f:
                tmpInf = await f.read()
            self.srvInf = toml.loads(tmpInf)
        else:
            await ctx.send('You have no permissions to execute this command.')

    @_settings.command(name='general')
    async def _settings_general(self, ctx, *, t: str):
        """ Set the channel name for general events """
        try:
            await self._save_serverinfo_file('general', ctx.guild.name, t)
            # self.srvInf['guilds'][ctx.guild.name]['channel_general'] = t.lower()
            # tomlStr = toml.dumps(self.srvInf)
            # async with aiofiles.open(self.DATA_PATH+self.INFO_FILE, mode='w') as f:
            #     await f.write(tomlStr)
            await ctx.channel.send(f'Changed the general events channel to {t.lower()}')
        except:
            await ctx.channel.send('**ERROR**: Could not change channel name')

    @_settings.command(name='amateur')
    async def _settings_amateur(self, ctx, *, t: str):
        """ Set the channel name for amateur events """
        try:
            await self._save_serverinfo_file('amateur', ctx.guild.name, t)
            # self.srvInf['guilds'][ctx.guild.name]['channel_amateur'] = t.lower()
            # tomlStr = toml.dumps(self.srvInf)
            # async with aiofiles.open(self.DATA_PATH+self.INFO_FILE, mode='w') as f:
            #     await f.write(tomlStr)
            await ctx.channel.send(f'Changed the amateur events channel to {t.lower()}')
        except:
            await ctx.channel.send('**ERROR**: Could not change channel name')

    @_settings.command(name='team')
    async def _settings_team(self, ctx, *, t: str):
        """ Set the channel name for team events """
        pass

    @_settings.command(name='osc')
    async def _settings_osc(self, ctx, *, t: str):
        """ Set the channel name for osc events """
        pass

    # @_settings.command(name='channel')
    # async def _settings_channel(self, ctx, *, t: str):
    #     """ Change the channel, the bot posts events in """
    #     s = t.split(' ')
    #     if len(s) == 2 and s[0].lower() in ['general', 'amateur', 'team']:
    #         self.srvInf['guilds'][ctx.guild.name][f'channel_{s[0].lower()}'] = s[1].lower()
    #         tomlStr = toml.dumps(self.srvInf)
    #         async with aiofiles.open(self.DATA_PATH+self.INFO_FILE, mode='w') as f:
    #             await f.write(tomlStr)
    #         await ctx.channel.send(f'Changed the {s[0].lower()} events channel to {s[1].lower()}')
    #     else:
    #         await ctx.channel.send('Error: only 2 arguments allowed.\n Arg 1: channel type (General, Amateur, Team) \nArg 2: channel-name')

    @_settings.command(name='time')
    async def _settings_time(self, ctx, *, t: int):
        """ Set the timeformat (24h- or 12ham/pm-format) """
        if len(t) == 1:
            if t in [12, 24]:
                self.srvInf['guilds'][ctx.guild.name]['timeformat'] = t
                tomlStr = toml.dumps(self.srvInf)
                async with aiofiles.open(self.DATA_PATH+self.INFO_FILE, mode='w') as f:
                    await f.write(tomlStr)
                await ctx.channel.send(f'Changed the time format to {t} hours')
            else:
                await ctx.channel.send('Error: time has to be either `12` or `24` hour format')

    @commands.command(name='list')
    async def _list_channels(self, ctx):
        gec = self.srvInf['guilds'][ctx.guild.name]['channel_general']
        aec = self.srvInf['guilds'][ctx.guild.name]['channel_amateur']
        await ctx.channel.send(f'The currently set SC2 event channels are\nGeneral events channel: `{gec}`\nAmateur events channel: `{aec}`')


def setup(bot):
    n = SC2OESettings(bot)
    bot.add_cog(n)
