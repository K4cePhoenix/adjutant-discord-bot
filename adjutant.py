from datetime import datetime
from discord.ext import commands
import aiofiles
import discord
import logging
import os
import platform
import pytz
import sys
import time
import toml
import traceback


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

        CONF_PATH = './data/bot/'
        CONF_NAME = 'conf.toml'
        self.CONFIG = toml.load(CONF_PATH+CONF_NAME)
        self.VERSION = self.CONFIG['owner']['version']
        self.START_TIME = datetime.now(tz=pytz.utc)


        dbuser = self.CONFIG['db']['user']
        dbpass = self.CONFIG['db']['pass']
        dbname = self.CONFIG['db']['name']
        dbhost = self.CONFIG['db']['host']
        dbcred = {"user": dbuser, "password": dbpass, "database": dbname, "host": dbhost}

        async def _init_db():
            self.db = await asyncpg.create_pool(**dbcred)
            await self.db.execute("CREATE TABLE IF NOT EXISTS guilds (id bigint primary key, name text, general bigint, amateur bigint, team bigint, osc bigint, feeds bigint, feedList text[], feedIds text[][], timeFormat boolean, );")

        # self.loop.create_task(_init_db())

        
        self.SC2DAT_PATH = './data/sc2oe/'
        self.EVTINF_FILE = 'evInf.toml'
        self.SRVINF_FILE = 'srvInf.toml'
        
        if os.path.isdir(self.SC2DAT_PATH) is False:
            os.makedirs(self.SC2DAT_PATH)
        if os.path.isfile(self.SC2DAT_PATH + self.SRVINF_FILE) is False:
            open(self.SC2DAT_PATH+self.SRVINF_FILE, 'a').close()
        if os.path.isfile(self.SC2DAT_PATH + self.EVTINF_FILE) is False:
            open(self.SC2DAT_PATH+self.EVTINF_FILE, 'a').close()
        self.srvInf = toml.load(self.SC2DAT_PATH + self.SRVINF_FILE)
        self.evInf = toml.load(self.SC2DAT_PATH + self.EVTINF_FILE)

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
        self.log.info(f'\nYou are running Adjutant DiscordBot/v{self.VERSION} by Phoenix#2694')
        self.log.info(f'Ready at {datetime.now(tz=pytz.utc):%b %d, %H:%M (%Z)}')
        await self.change_presence(activity=discord.Activity(name='a> | b', type=discord.ActivityType.watching))
        chan = self.get_channel(436581310379720705)
        embed = discord.Embed(color=discord.Color.blue(), title="Adjutant ready!")#All shards ready!")
        try:
            await chan.send(embed=embed)
        except:
            pass

    # async def on_shard_ready(self, id):
    #     chan = self.get_channel(477110208225738752)
    #     embed = discord.Embed(color=discord.Color.blue(), title=f"Shard {id} ready!")
    #     try:
    #         await chan.send(embed=embed)
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

        chan = self.get_channel(477110208225738752)
        embed = discord.Embed(color=discord.Color.green(), title="Established new connection.", description=f"Now connected to {len(self.guilds)} guilds!")
        embed.set_thumbnail(url=guild.icon_url)
        embed.add_field(name="Name", value=guild.name)
        embed.add_field(name="Owner", value=guild.owner)
        embed.add_field(name="Members", value=guild.member_count)
        embed.add_field(name="Creation date", value=guild.created_at.strftime('%Y/%m/%d'))
        try:
            msg = await chan.send(embed=embed)
        except:
            pass

        self.log.info(f"Joined the {guild.name} guild")

        # INSERT DATABASE CONTENT HERE
        try:
            self.srvInf['guilds'][guild.name] = {'name': guild.name, 'id': guild.id, 'channel_general': "", 'channel_amateur': "", 'channel_team': "", 'timeformat': 12}
            tomlStr = toml.dumps(self.srvInf)
            async with aiofiles.open(self.SC2DAT_PATH+self.SRVINF_FILE, mode='w') as f:
                await f.write(tomlStr)
            await msg.add_reaction('☑')
        except Exception:
            self.log.error("on_guild_join: Couldn't save server info file.")
            traceback.print_exc()
            pass


    async def on_guild_remove(self, guild):
        chan = self.get_channel(477110208225738752)
        embed = discord.Embed(color=discord.Color.red(), title="Lost contact to a guild...", description=f"{len(self.guilds)} guild relays remaining.")
        embed.set_thumbnail(url=guild.icon_url)
        embed.add_field(name="Name", value=guild.name)
        embed.add_field(name="Owner", value=guild.owner)
        embed.add_field(name="Members", value=guild.member_count)
        embed.add_field(name="Creation date", value=guild.created_at.strftime('%Y/%m/%d'))
        try:
            msg = await chan.send(embed=embed)
        except:
            pass

        self.log.info(f"Left the {guild.name} guild")

        # INSERT DATABASE CONTENT HERE
        try:
            self.srvInf['guilds'].pop(guild.name, None)
            async with aiofiles.open(self.SC2DAT_PATH+self.SRVINF_FILE, mode='w') as f:
                tomlStr = toml.dumps(self.srvInf)
                await f.write(tomlStr)
            await msg.add_reaction('☑')
        except Exception:
            self.log.error("on_guild_join: Couldn't save server info file.")
            traceback.print_exc()
            pass

bot = Adjutant()
CONF_PATH = './data/bot/'
CONF_NAME = 'conf.toml'
if os.path.isdir(CONF_PATH) is False:
    print(f'Could not find folder {CONF_PATH}')
elif os.path.isfile(CONF_PATH+CONF_NAME) is False:
    print(f'Could not find config file in {CONF_PATH}')
else:
    config = toml.load(CONF_PATH+CONF_NAME)
bot.run(config['owner']['token'])
