from datetime import datetime
from discord.ext import commands
import discord
import logging
import os
import platform
import pytz
import sys
import time
import toml


def _get_prefix(bot, message):
    """ A callable Prefix for our bot.
    This could be edited to allow per server prefixes.
    In direct messages, only one prefix is allowed, while in a server,
    the user is allowed to mention us or use any of the prefixes in our list.
    """
    prefixes = ['a>', 'adjutant ', 'a!']
    if not message.guild:
        return '!'
    return commands.when_mentioned_or(*prefixes)(bot, message)

class Adjutant(commands.Bot):#AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=_get_prefix,
                         description="Adjutant 10-32 Discord Bot by Phoenix#2694",
                         pm_help=None,
                         status=discord.Status.dnd,
                         activity=discord.Game(name="Restarting..."),
                         case_insensitive=True)

        conf_path = './data/bot/'
        conf_name = 'conf.toml'
        self.config = toml.load(conf_path+conf_name)
        self.version = self.config['owner']['version']

        self.remove_command('help')

        self.log = logging.getLogger('adjutant')
        self.log.setLevel(logging.INFO)
        self.handler = logging.FileHandler(filename='adjutant.log', encoding='utf-8', mode='w')
        self.log.addHandler(self.handler)

        for file in os.listdir("ext"):
            if file.endswith(".py"):
                name = file[:-3]
                try:
                    self.load_extension(f"ext.{name}")
                    print(name + ' loaded.')
                    self.log.info(f'Loaded extension {name}')
                except Exception as e:
                    exc = f'{type(e).__name__}: {e}'
                    print(name + ' failed to load.')
                    self.log.error(f'Failed to load extension {name} - {exc}')

    async def on_ready(self):
        guilds = len(self.guilds)
        channels = len([key for key in self.get_all_channels()])
        users = len(set(self.get_all_members()))
        self.log.info(f'Logged in as {self.user.name} (ID: {self.user.id})')
        self.log.info('Connected to:')
        self.log.info(f'{guilds} guilds | {channels} channels | {users} users\n')
        self.log.info(f'Current Discord.py Version: {discord.__version__} | Current Python Version: {platform.python_version()}')
        self.log.info(f'\nUse this link to invite {self.user.name}:')
        self.log.info(f'https://discordapp.com/oauth2/authorize?client_id={self.user.id}&scope=bot')
        self.log.info('\nYou are running Adjutant 10-32 Discord Bot by Phoenix#2694')
        self.log.info(f'Ready at {datetime.now(tz=pytz.utc):%b %d, %H:%M (%Z)}')
        await self.change_presence(activity=discord.Activity(name='a> | b', type=discord.ActivityType.watching))
        c = self.get_channel(436581310379720705)
        e = discord.Embed(color=discord.Color.blue(), title="Adjutant ready!")#All shards ready!")
        try:
            await c.send(embed=e)
        except:
            pass

    # async def on_shard_ready(self, id):
    #     c = self.get_channel(477110208225738752)
    #     e = discord.Embed(color=discord.Color.blue(), title=f"Shard {id} ready!")
    #     try:
    #         await c.send(embed=e)
    #     except:
    #         pass

    async def on_message(self, msg):
        if not msg.author.bot:
            await self.process_commands(msg)

    async def on_command(self, ctx):
        message = ctx.message
        destination = None
        if isinstance(ctx.channel, discord.abc.GuildChannel):
            destination = 'Private Message'
        else:
            destination = f'#{message.channel.name} ({message.guild.name})'
        self.log.info(f'{message.created_at}: {message.author.name} in {destination}: {message.content}')

    async def on_guild_join(self, guild):
        if guild.me.guild_permissions.change_nickname:
            await guild.me.edit(nick='Adjutant 10-32')
        else:
            self.log.info(f"Couldn't change my name on {guild.name}")

        # INSERT DATABASE CONTENT HERE

        c = self.get_channel(436581310379720705)
        e = discord.Embed(color=discord.Color.green(), title="New guild!", description=f"We're now in {len(self.guilds)} guilds!")
        e.set_thumbnail(url=guild.icon_url)
        e.add_field(name="Name", value=guild.name)
        e.add_field(name="Owner", value=guild.owner)
        e.add_field(name="Members", value=guild.member_count)
        try:
            await c.send(embed=e)
        except:
            pass

    async def on_guild_remove(self, guild):

        # INSERT DATABASE CONTENT HERE

        c = self.get_channel(436581310379720705)
        e = discord.Embed(color=discord.Color.red(), title="We lost a guild...", description=f"But it's okay, we're still in {len(self.guilds)} other guilds!")
        e.set_thumbnail(url=guild.icon_url)
        e.add_field(name="Name", value=guild.name)
        e.add_field(name="Owner", value=guild.owner)
        e.add_field(name="Members", value=guild.member_count)
        try:
            await c.send(embed=e)
        except:
            pass

    async def restart_adjutant(self):
        sys.exit(1)


bot = Adjutant()
conf_path = './data/bot/'
conf_name = 'conf.toml'
if os.path.isdir(conf_path) is False:
    print(f'Could not find folder {conf_path}')
elif os.path.isfile(conf_path+conf_name) is False:
    print(f'Could not find config file in {conf_path}')
else:
    config = toml.load(conf_path+conf_name)
bot.run(config['owner']['token'])
