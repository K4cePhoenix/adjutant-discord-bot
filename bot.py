from datetime import datetime, timedelta
from discord.ext import commands
import asyncio
import discord
import logging
import os
import platform
import pytz
import toml


""" SC2 Event Bot
posts informations of open sc2 tournaments.
"""

def get_prefix(bot, message):
    """ A callable Prefix for our bot.
    This could be edited to allow per server prefixes.
    In direct messages, only one prefix is allowed, while in a server,
    the user is allowed to mention us or use any of the prefixes in our list.
    """
    prefixes = ['a>', 'Adjutant ', 'adjutant ', 'a!']
    if (not message.guild):
        return '!'
    return commands.when_mentioned_or(*prefixes)(bot, message)

initial_extensions = ['ext.sc2openevents',
                      'ext.quotes']

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')
logger.addHandler(handler)

bot = commands.Bot(description=('Adjutant 10-32 Discord Bot by Phoenix#2694'), command_prefix=get_prefix)

@bot.event
async def on_ready():
    guilds = len(bot.guilds)
    channels = len([key for key in bot.get_all_channels()])
    users = len(set(bot.get_all_members()))
    print('Logged in as {} (ID: {})'.format(bot.user.name, bot.user.id))
    print('\nConnected to:')
    print('{} guilds | {} channels | {} users\n'.format(guilds, channels, users))
    print('------------------------')
    print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__, platform.python_version()))
    print('\nUse this link to invite {}:'.format(bot.user.name))
    print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot'.format(bot.user.id))
    print('------------------------')
    print('You are running SC2 Events Bot v'+conf['owner']['version']+' by Phoenix#2694')
    print('Ready at  {:%b %d, %H:%M (%Z)}'.format(datetime.now(tz=pytz.utc)))
    await bot.change_presence(activity=discord.Game(name='with bugs..'))
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
            logger.info('Loaded extension {}'.format(extension))
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            logger.error('Failed to load extension {} - {}'.format(extension, exc))


@bot.event
async def on_guild_join(guild):
    if guild.me.guild_permissions.change_nickname:
        await guild.me.edit(nick='Adjutant 10-32')
    else:
        print("Couldn't change my name on {}".format(guild.name))


@bot.event
async def on_command(ctx):
    message = ctx.message
    destination = None
    if isinstance(ctx.channel, discord.abc.GuildChannel):
        destination = 'Private Message'
    else:
        destination = '#{0.channel.name} ({0.guild.name})'.format(message)
    logger.info('{0.created_at}: {0.author.name} in {1}: {0.content}'.format(message, destination))


if __name__ == '__main__':


    conf_path = './data/bot/'
    conf_name = 'conf.toml'
    if os.path.isdir(conf_path) is False:
        logger.critical('Could not find folder {}'.format(conf_path))
    elif os.path.isfile(conf_path+conf_name) is False:
        logger.critical('Could not find config file in {}'.format(conf_path))
    else:
        conf = toml.load(conf_path+conf_name)
        bot.run(conf['owner']['token'])
    handlers = logger.handlers[:]
    for hdlr in handlers:
        hdlr.close()
        logger.removeHandler(hdlr)
