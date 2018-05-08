from datetime import datetime
from discord.ext import commands
import discord
import logging
import os
import platform
import pytz
import time
import toml


""" SC2 Event Bot
posts informations of open sc2 tournaments.
"""

def get_prefix(adjutant, message):
    """ A callable Prefix for our bot.
    This could be edited to allow per server prefixes.
    In direct messages, only one prefix is allowed, while in a server,
    the user is allowed to mention us or use any of the prefixes in our list.
    """
    prefixes = ['a>', 'Adjutant ', 'adjutant ', 'a!']
    if (not message.guild):
        return '!'
    return commands.when_mentioned_or(*prefixes)(adjutant, message)

initial_extensions = ['ext.sc2oe_main',
                      'ext.sc2oe_settings',
                      'ext.rss']

logger = logging.getLogger('adjutant')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')
logger.addHandler(handler)

adjutant = commands.Bot(description=('Adjutant 10-32 Discord Bot by Phoenix#2694'), command_prefix=get_prefix)

@adjutant.event
async def on_ready():
    guilds = len(adjutant.guilds)
    channels = len([key for key in adjutant.get_all_channels()])
    users = len(set(adjutant.get_all_members()))
    print(f'Logged in as {adjutant.user.name} (ID: {adjutant.user.id})')
    print('\nConnected to:')
    print(f'{guilds} guilds | {channels} channels | {users} users\n')
    print('------------------------')
    print(f'Current Discord.py Version: {discord.__version__} | Current Python Version: {platform.python_version()}')
    print(f'\nUse this link to invite {adjutant.user.name}:')
    print(f'https://discordapp.com/oauth2/authorize?client_id={adjutant.user.id}&scope=bot')
    print('------------------------')
    print('You are running SC2 Events Bot v'+conf['owner']['version']+' by Phoenix#2694')
    print('Ready at  {:%b %d, %H:%M (%Z)}'.format(datetime.now(tz=pytz.utc)))
    await adjutant.change_presence(activity=discord.Game(name='with bugs..'))
    for extension in initial_extensions:
        try:
            adjutant.load_extension(extension)
            logger.info(f'Loaded extension {extension}')
        except Exception as e:
            exc = f'{type(e).__name__}: {e}'
            logger.error(f'Failed to load extension {extension} - {exc}')


@adjutant.event
async def on_guild_join(guild):
    if guild.me.guild_permissions.change_nickname:
        await guild.me.edit(nick='Adjutant 10-32')
    else:
        print(f"Couldn't change my name on {guild.name}")


@adjutant.event
async def on_command(ctx):
    message = ctx.message
    destination = None
    if isinstance(ctx.channel, discord.abc.GuildChannel):
        destination = 'Private Message'
    else:
        destination = f'#{message.channel.name} ({message.guild.name})'
    logger.info(f'{message.created_at}: {message.author.name} in {destination}: {message.content}')


@adjutant.command(name='ping')
async def _ping(ctx):
        pingtime = time.time()
        e = discord.Embed(title="Pinging...", colour=0xFF0000)
        msg = await ctx.send (embed=e)
        ping = time.time() - pingtime
        complete = "Pong, %.01f seconds" % ping
        em = discord.Embed(title=complete, colour=0xFF0000)
        await msg.edit(embed=em)


if __name__ == '__main__':
    conf_path = './data/bot/'
    conf_name = 'conf.toml'
    if os.path.isdir(conf_path) is False:
        logger.critical(f'Could not find folder {conf_path}')
        elif os.path.isfile(conf_path+conf_name) is False:
        logger.critical(f'Could not find config file in {conf_path}')
    else:
        conf = toml.load(conf_path+conf_name)
        adjutant.run(conf['owner']['token'])
    handlers = logger.handlers[:]
    for hdlr in handlers:
        hdlr.close()
        logger.removeHandler(hdlr)
