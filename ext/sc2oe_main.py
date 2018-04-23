from datetime import datetime, timedelta
from discord.ext import commands
import asyncio
import discord
import logging
import os
import pytz
import toml

from .sc2 import kuevst
from .utils.chat_formatting import *

log = logging.getLogger(__name__)


class SC2OpenEvents():
    def __init__(self, bot):
        self.bot = bot
        self.data_path = './data/sc2oe/'
        self.info_file = 'srvInf.toml'
        self.code_file = 'codes.toml'
        if os.path.isdir(self.data_path) is False:
            os.makedirs(self.data_path)
        if os.path.isfile(self.data_path + self.info_file) is False:
            open(self.data_path+self.info_file, 'a').close()
        if os.path.isfile(self.data_path + self.code_file) is False:
            open(self.data_path+self.code_file, 'a').close()
        self.srvInf = toml.load(self.data_path + self.info_file)
        self.codes = toml.load(self.data_path + self.code_file)

    async def del_old_events(self, events, msgs, srv, ch, eventType, x):
        dEvCount = 0
        for y in range(0, len(events[x])):
            for ev in range(0, len(msgs)):
                for channel in srv.channels:
                    if events[x][y][0] == msgs[ev].content.split('**')[1] and ((events[x][y][9].days * 24) + (events[x][y][9].seconds / (60 * 60))) <= 0:
                        for s in self.srvInf['guilds']:
                            if srv.name == self.srvInf['guilds'][s]['name'] and channel.name == self.srvInf['guilds'][s]['ch_{}'.format(eventType)] and channel.permissions_for(srv.me).manage_messages:
                                dEvCount += 1
                                msgs[ev].delete()
        log.info('{} ended events detected'.format(dEvCount))
        return

    async def send_event_update(self, msg, srv, eventType):
        for channel in srv.channels:
            for s in self.srvInf['guilds']:
                if srv.name == self.srvInf['guilds'][s]['name'] and channel.name == self.srvInf['guilds'][s]['ch_{}'.format(eventType)] and channel.permissions_for(srv.me).send_messages:
                    await channel.send(msg)
                    log.info('{}, {} - sent {}'.format(srv, channel, msg))

    async def post_eligible_events(self, tLimit, events, msgs, srv, ch, eventType, x):
        aEvCount = 0
        pEvCount = 0
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
                msg = inline('[EVENT]') + ' ' + bold(events[x][y][0])
                msg += '\n\nTime: ' + events[x][y][1]
                if (x != 1) and (events[x][y][3] == None):
                    msg += '\nRegion: {}'.format(events[x][y][2])
                elif (x == 1) and (events[x][y][3] != None):
                    msg += '\nLeague: {}'.format(events[x][y][3])
                if events[x][y][4] != None:
                    msg += '\nServer: {}'.format(events[x][y][4])
                if events[x][y][10] != None:
                    msg += '\nMode: {}'.format(events[x][y][10])
                if events[x][y][5] != None:
                    msg += '\nPrizepool: {}'.format(events[x][y][5])
                if events[x][y][6] != None:
                    eventName = '_'.join(events[x][y][0].split(' ')[:len(events[x][y][0].split(' '))-1])
                    if any(char.isdigit() for char in events[x][y][7]) == False and events[x][y][7] != None and eventName in self.codes.keys():
                        tmpStr = events[x][y][0].split(' ')[-1].replace("#", "")
                        codeNr = tmpStr.replace(".", "")
                        events[x][y][7] = self.codes[eventName]['code'].replace("$", str(codeNr))
                    msg += '\nMatcherino: ' + nopreview(events[x][y][6])
                    msg += ' - free $1 code {}'.format(inline(events[x][y][7]))
                if events[x][y][8] != None:
                    msg += '\nSign ups: {}'.format(events[x][y][8])
                msg = box(msg)
                await self.send_event_update(msg, srv, eventType)
        log.info('{0} / {1}  {3} events already posted in {2.name}'.format(pEvCount, aEvCount, srv, eventType))

    async def check_posted_events(self, tLimit, events, eventType, x):
        for guild in self.bot.guilds:
            msgs = []
            ch = []
            print('processing {} events in {}'.format(eventType, guild.name))
            for channel in guild.channels:
                for s in self.srvInf['guilds']:
                    if (guild.name == self.srvInf['guilds'][s]['name']) and (
                            channel.name == self.srvInf['guilds'][s]['ch_{}'.format(eventType)]) and channel.permissions_for(
                                guild.me).read_messages:
                        async for message in channel.history():
                            msgs.append(message)
                            ch.append(channel)
            await self.post_eligible_events(tLimit, events, msgs, guild, ch, eventType, x)

    async def check_all_events(self, tLimit):
        events = [[], [], []]
        events[0] = kuevst.steal('general')
        events[1] = kuevst.steal('amateur')
        events[2] = kuevst.steal('team')
        log.info('Fetched {0} general, {1} amateur and {2} team events'.format(len(events[0]), len(events[1]), len(events[2])))
        for x in range (0, len(events)):
            if x == 0:
                await self.check_posted_events(tLimit, events, 'general', x)
            elif x == 1:
                await self.check_posted_events(tLimit, events, 'amateur', x)
            elif x == 2:
                await self.check_posted_events(tLimit, events, 'team', x)
            else:
                log.critical('EVENT LIST ERROR?!')

    async def check_events_in_background(self):
        await self.bot.wait_until_ready()
        while True:
            self.srvInf = toml.load(self.data_path + self.info_file) # reload srvInf in case it updated
            await self.check_all_events(float(self.srvInf['general']['countdown']))
            nextUpdateTime = datetime.now(tz=pytz.utc) + timedelta(hours=float(self.srvInf['general']['delay']))
            log.info('Next event check at {:%b %d, %H:%M (%Z)}'.format(nextUpdateTime))
            await asyncio.sleep(float(self.srvInf['general']['delay']) * 60 * 60)


def setup(bot):
    n = SC2OpenEvents(bot)
    bot.add_cog(n)
    bot.loop.create_task(n.check_events_in_background())