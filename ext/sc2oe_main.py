from datetime import datetime, timedelta
from discord.ext import commands
from random import choice as randchoice
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
    def __init__(self, adjutant):
        self.adjutant = adjutant
        self.data_path = './data/sc2oe/'
        self.serverinfo_file = 'srvInf.toml'
        self.eventinfo_file = 'evInf.toml'
        if os.path.isdir(self.data_path) is False:
            os.makedirs(self.data_path)
        if os.path.isfile(self.data_path + self.serverinfo_file) is False:
            open(self.data_path+self.serverinfo_file, 'a').close()
        if os.path.isfile(self.data_path + self.eventinfo_file) is False:
            open(self.data_path+self.eventinfo_file, 'a').close()
        self.srvInf = toml.load(self.data_path + self.serverinfo_file)
        self.evInf = toml.load(self.data_path + self.eventinfo_file)


    async def del_old_events(self, msg):
        print('Delete message\nID: {}\nName: {}'.format(msg.id, msg.embeds[0].title))
        if msg.channel.permissions_for(msg.guild.me).manage_messages:
            await msg.delete()


    async def send_event_update(self, oldMsg, msg, em):
        if oldMsg.channel.permissions_for(oldMsg.guild.me).manage_messages:
            await oldMsg.edit(content=msg, embed=em)
            log.info('{}, {} - deleted {}'.format(oldMsg.guild, oldMsg.channel, em.title))


    async def send_event(self, msg, em, srv, evType):
        for channel in srv.channels:
            for s in self.srvInf['guilds']:
                if srv.name == self.srvInf['guilds'][s]['name'] and channel.name == self.srvInf['guilds'][s]['channel_{}'.format(evType)] and channel.permissions_for(srv.me).send_messages:
                    await channel.send(msg, embed=em)
                    log.info('{}, {} - sent {}'.format(srv, channel, em.title))


    async def post_events(self, eventsX, msgs, srv, ch, evType):
        aEvCount = 0
        pEvCount = 0
        dEvCount = 0
        for y in range(0, len(eventsX)):
            if eventsX[y][9] != None:
                countdown = (eventsX[y][9].days * 24) + (eventsX[y][9].seconds / (60 * 60))
            else:
                countdown = -1.0
            p = True
            for ev in range(0, len(msgs)):
                if msgs[ev].embeds:
                    if eventsX[y][0] == msgs[ev].embeds[0].title:
                        p = False
                        aEvCount += 1
                        pEvCount += 1
                        pMsg = msgs[ev]
                        break
            if (0 < countdown < float(self.srvInf['general']['countdown'])):
                aEvCount += 1
                cd_hours = eventsX[y][9].seconds // (60 * 60)
                cd_minutes = (eventsX[y][9].seconds-(cd_hours * (60 * 60))) // 60
                evName = '_'.join(eventsX[y][0].split(' ')[:len(eventsX[y][0].split(' '))-1])

                em = discord.Embed(title=eventsX[y][0], colour=discord.Colour(int('0x{}'.format(randchoice(self.evInf['Other']['colours'])), 16)), description="{}".format(eventsX[y][1]))

                if evType == 'general':
                    msg = 'General Event is happening in {}h {}min'.format(cd_hours, cd_minutes)
                    em.set_author(name="General Event", icon_url="http://liquipedia.net/commons/images/7/75/GrandmasterMedium.png")
                elif evType == 'amateur':
                    msg = 'Amateur Event is happening in {}h {}min'.format(cd_hours, cd_minutes)
                    if 'Master' in eventsX[y][3]:
                        em.set_author(name="Amateur Event", icon_url="http://liquipedia.net/commons/images/2/26/MasterMedium.png")
                    elif 'Diamond' in eventsX[y][3]:
                        em.set_author(name="Amateur Event", icon_url="http://liquipedia.net/commons/images/9/90/DiamondMedium.png")
                    elif 'Platinum' in eventsX[y][3]:
                        em.set_author(name="Amateur Event", icon_url="http://liquipedia.net/commons/images/2/2b/PlatinumMedium.png")
                    elif 'Gold' in eventsX[y][3]:
                        em.set_author(name="Amateur Event", icon_url="http://liquipedia.net/commons/images/5/55/GoldMedium.png")
                    elif 'Silver' in eventsX[y][3]:
                        em.set_author(name="Amateur Event", icon_url="http://liquipedia.net/commons/images/2/22/SilverMedium.png")
                    elif 'Bronze' in eventsX[y][3]:
                        em.set_author(name="Amateur Event", icon_url="http://liquipedia.net/commons/images/c/cb/BronzeMedium.png")
                    else:
                        em.set_author(name="Amateur Event", icon_url="https://i.imgur.com/HlsskVP.png")
                elif evType == 'team':
                    pass

                if evName in self.evInf.keys() and self.evInf[evName]['logo']:
                    em.set_thumbnail(url=self.evInf[evName]['logo'])
                else:
                    em.set_thumbnail(url=self.evInf['Other']['logo'])

                if (evType == 'general') and (eventsX[y][2] != None):
                    em.add_field(name="Region", value=eventsX[y][2], inline=True)
                elif (evType == 'amateur') and (eventsX[y][3] != None):
                    em.add_field(name="League", value=eventsX[y][3], inline=True)

                if eventsX[y][4]:
                    em.add_field(name="Server", value=eventsX[y][4], inline=True)
                if eventsX[y][5]:
                    em.add_field(name="Prizepool", value=eventsX[y][5], inline=False)

                if eventsX[y][6]:
                    if any(char.isdigit() for char in eventsX[y][7]) == False and eventsX[y][7] == None and evName in self.evInf.keys():
                        codeNr = eventsX[y][0].split(' ')[-1].replace("#", "").replace(".", "")
                        eventsX[y][7] = self.evInf[evName]['code'].replace("$", str(codeNr))
                    cfVal = "[Matcherino]({}) - free $1 code `{}`".format(eventsX[y][6], eventsX[y][7])
                if evName in self.evInf.keys():
                    if self.evInf[evName]['patreon']:
                        if cfVal: 
                            cfVal += "\n[Patreon]({}) - contribute to increase the prize pool".format(self.evInf[evName]['patreon'])
                        else: 
                            cfVal = "[Patreon]({}) - contribute to increase the prize pool".format(self.evInf[evName]['patreon'])
                try:
                    em.add_field(name="Crowdfunding", value=cfVal, inline=False)
                except:
                    pass

                if eventsX[y][8]:
                    em.add_field(name='▬▬▬▬▬▬▬', value='[**SIGN UP HERE**]({})'.format(eventsX[y][8]), inline=False)

                #em.set_footer(text="Adjutant Discord Bot by Phoenix#2694")

                if p:
                    await self.send_event(msg, em, srv, evType)
                elif not p:
                    await self.send_event_update(pMsg, msg, em)
            elif (countdown < -float(self.srvInf['general']['deleteDelay'])) and not p:
                dEvCount += 1
                await self.del_old_events(pMsg)
        log.info('{0} / {1}  {3} events already posted and {4} got deleted in {2.name}'.format(pEvCount, aEvCount, srv, evType, dEvCount))


    async def check_all_events(self):
        events = [[], [], []]
        events[0] = kuevst.steal('general')
        events[1] = kuevst.steal('amateur')
        #events[2] = kuevst.steal('team')
        log.info('Fetched {0} general, {1} amateur and {2} team events'.format(len(events[0]), len(events[1]), len(events[2])))
        for guild in self.adjutant.guilds:
            msgs = []
            chan = []
            for x in range(0, len(events)):
                if x == 0:
                    evType = 'general'
                elif x == 1:
                    evType = 'amateur'
                elif x == 2:
                    evType = 'team'
                log.info('processing {} events in {}'.format(evType, guild.name))
                print('processing {} events in {}'.format(evType, guild.name))
                for channel in guild.channels:
                    for srv in self.srvInf['guilds']:
                        if (guild.name == srv) and (channel.name == self.srvInf['guilds'][srv]['channel_{}'.format(evType)]) and channel.permissions_for(guild.me).read_messages:
                            async for message in channel.history():
                                msgs.append(message)
                                chan.append(channel)
                await self.post_events(events[x], msgs, guild, chan, evType)


    async def check_events_in_background(self):
        await self.adjutant.wait_until_ready()
        while True:
            self.srvInf = toml.load(self.data_path + self.serverinfo_file)
            await self.check_all_events()
            nextUpdateTime = datetime.now(tz=pytz.utc) + timedelta(hours=float(self.srvInf['general']['sleepDelay']))
            log.info('Next event check at {:%b %d, %H:%M (%Z)}'.format(nextUpdateTime))
            await asyncio.sleep(float(self.srvInf['general']['sleepDelay']) * 60 * 60)


def setup(adjutant):
    n = SC2OpenEvents(adjutant)
    adjutant.add_cog(n)
    adjutant.loop.create_task(n.check_events_in_background())
