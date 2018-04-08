from datetime import datetime, timedelta
from discord.ext import commands
import asyncio
import discord
import logging
import os
import platform
import pytz
import toml

from .sc2 import kuevst
from .utils.chat_formatting import *

log = logging.getLogger(__name__)


class SC2OpenEvents():
    def __init__(self, bot):
        self.bot = bot
        self.data_path = './data/sc2oe/'
        self.file_name = 'srvInf.toml'
        if os.path.isdir(self.data_path) is False:
            os.makedirs(self.data_path)
        if os.path.isfile(self.data_path + self.file_name) is False:
            open(self.data_path+self.file_name, 'a').close()
        self.conf = toml.load(self.data_path + self.file_name)

    async def del_old_events(self, events, msgs, srv, ch):
        dEvCount = 0
        for x in range(0, len(events)):
            for y in range(0, len(events[x])):
                for ev in range(0, len(msgs)):
                    for channel in srv.channels:
                        if events[x][y][0] == msgs[ev].content.split('**')[1] and ((events[x][y][9].days * 24) + (events[x][y][9].seconds / (60 * 60))) <= 0:
                            for s in range(0, len(self.conf['guilds'])):
                                if srv.name == self.conf['guilds'][str(s)]['name'] and channel.name == self.conf['guilds'][str(s)]['channel'] and channel.permissions_for(srv.me).manage_messages:
                                    dEvCount += 1
                                    msgs[ev].delete()
        print(str(dEvCount) + ' ended events detected')
        return

    async def send_event_update(self, msg, srv):
        for channel in srv.channels:
            for s in range(0, len(self.conf['guilds'])):
                if srv.name == self.conf['guilds'][str(s)]['name'] and channel.name == self.conf['guilds'][str(s)]['channel'] and channel.permissions_for(srv.me).send_messages:
                    await channel.send(msg)
                    log.info('{}, {} - sent {}'.format(srv, channel, msg))

    async def post_eligible_events(self, tLimit, events, msgs, srv, ch):
        aEvCount = 0
        pEvCount = 0
        for x in range(0, len(events)):
            for y in range(0, len(events[x])):
                cdH = (events[x][y][9].days * 24) + (events[x][y][9].seconds / (60 * 60))
                p = True
                for ev in range(0, len(msgs)):
                    if len(msgs[ev].content.split('**')) > 1:
                        if events[x][y][0] == msgs[ev].content.split('**')[1]:
                            p = False
                            aEvCount += 1
                            pEvCount += 1
                if (0 < cdH < tLimit) and p:
                    aEvCount += 1
                    msg = inline('[EVENT]') + ' ' + bold(events[x][y][0]) + '\n\n'
                    msg += 'Time: ' + events[x][y][1] + '\n'
                    if (x != 1) and (events[x][y][3] == None):
                        msg += 'Region: {}\n'.format(events[x][y][2])
                    elif (x == 1) and (events[x][y][3] != None):
                        msg += 'League: {}\n'.format(events[x][y][3])
                    if events[x][y][4] != None:
                        msg += 'Server: {}\n'.format(events[x][y][4])
                    if events[x][y][10] != None:
                        msg += 'Mode: {}\n'.format(events[x][y][10])
                    if events[x][y][5] != None:
                        msg += 'Prizepool: {}\n'.format(events[x][y][5])
                    if events[x][y][6] != None:
                        msg += 'Matcherino: ' + nopreview(events[x][y][6])
                        #if events[x][y][7] != None:
                        msg += ' - free $1 code {}'.format(inline(events[x][y][7]))
                        msg += '\n'
                    if events[x][y][8] != None:
                        msg += 'Sign ups: {}\n'.format(events[x][y][8])
                        msg = box(msg)
                    await self.send_event_update(msg, srv)
        print(((str(pEvCount) + ' / ') + str(aEvCount)) + ' events already posted')
        log.info('{0} / {1} events already posted in {2.name}'.format(pEvCount, aEvCount, srv))

    async def check_posted_events(self, tLimit, events):
        for guild in self.bot.guilds:
            msgs = []
            ch = []
            print('processing server: ' + guild.name)
            for channel in guild.channels:
                for s in range(0, len(self.conf['guilds'])):
                    if (guild.name == self.conf['guilds'][str(s)]['name']) and (
                            channel.name == self.conf['guilds'][str(s)]['channel']) and channel.permissions_for(
                                guild.me).read_messages:
                        async for message in channel.history():
                            msgs.append(message)
                            ch.append(channel)
            await self.post_eligible_events(tLimit, events, msgs, guild, ch)

    async def check_all_events(self, tLimit):
        events = [[], [], []]
        events[0] = kuevst.steal('general')
        events[1] = kuevst.steal('amateur')
        events[2] = kuevst.steal('team')
        print('fetched {1} general, {1} amateur and {2} team events'.format(
            len(events[0]), len(events[1]), len(events[2])))
        print('checking event history')
        await self.check_posted_events(tLimit, events)

    async def check_events_in_background(self):
        await self.bot.wait_until_ready()
        while True:
            waitDelay = 1.0
            maxEvCountDown = 25.0
            print('checking events')
            await self.check_all_events(maxEvCountDown)
            nextUpdateTime = datetime.now(tz=pytz.utc) + timedelta(hours=waitDelay)
            print('next event check at {:%b %d, %H:%M (%Z)}'.format(nextUpdateTime))
            await asyncio.sleep((waitDelay * 60) * 60)


def setup(bot):
    n = SC2OpenEvents(bot)
    bot.add_cog(n)
    bot.loop.create_task(n.check_events_in_background())
