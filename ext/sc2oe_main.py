from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import aiohttp
import asyncio
import discord
import logging
import os
import pytz
import toml

from .sc2 import kuevst

log = logging.getLogger('adjutant.sc2oe')


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
        if msg.channel.permissions_for(msg.guild.me).manage_messages:
            await msg.delete()
            log.info(f'{msg.guild}, {msg.channel} - deleted {msg.embeds[0].title}')


    async def send_event_update(self, oldMsg, msg, em):
        if oldMsg.channel.permissions_for(oldMsg.guild.me).manage_messages:
            await oldMsg.edit(content=msg, embed=em)
            log.info(f'{oldMsg.guild}, {oldMsg.channel} - updated {em.title}')


    async def send_event(self, msg, em, srv, evType):
        for channel in srv.channels:
            for s in self.srvInf['guilds']:
                if srv.name == self.srvInf['guilds'][s]['name'] and channel.name == self.srvInf['guilds'][s][f'channel_{evType}'] and channel.permissions_for(srv.me).send_messages:
                    await channel.send(msg, embed=em)
                    log.info(f'{srv}, {channel} - sent {em.title}')
                    return


    async def post_events(self, eventsX, msgs, srv, ch, evType):
        aEvCount = 0
        pEvCount = 0
        dEvCount = 0
        for eventXY in eventsX:
            if eventXY[9] != None:
                countdown = (eventXY[9].days * 24) + (eventXY[9].seconds / (60 * 60))
            else:
                countdown = -1.0
            p = True
            for MsgsEv in msgs:
                if MsgsEv.embeds:
                    if eventXY[0] == MsgsEv.embeds[0].title:
                        p = False
                        aEvCount += 1
                        pEvCount += 1
                        pMsg = MsgsEv
                        break
            if 0 < countdown < float(self.srvInf['general']['countdown']):
                aEvCount += 1
                cd_hours = eventXY[9].seconds // (60 * 60)
                cd_minutes = (eventXY[9].seconds-(cd_hours * (60 * 60))) // 60
                evName = '_'.join(eventXY[0].split(' ')[:len(eventXY[0].split(' '))-1])

                if evName in self.evInf.keys() and self.evInf[evName]['colour']:
                    em = discord.Embed(title=eventXY[0], colour=discord.Colour(int(self.evInf[evName]['colour'], 16)), description="{}".format(eventXY[1]))
                else:
                    em = discord.Embed(title=eventXY[0], colour=discord.Colour(0x555555), description="{}".format(eventXY[1]))

                msg = f'{evType} Event is happening in {cd_hours}h {cd_minutes}min'
                if evType == 'General':
                    em.set_author(name=f"{evType} Event", icon_url="https://i.imgur.com/lTur4HM.png")
                elif evType == 'Amateur':
                    if 'Master' in eventXY[3]:
                        em.set_author(name=f"{evType} Event", icon_url="https://i.imgur.com/R3M8AlH.png")
                    elif 'Diamond' in eventXY[3]:
                        em.set_author(name=f"{evType} Event", icon_url="https://i.imgur.com/i3ceEMq.png")
                    elif 'Platinum' in eventXY[3]:
                        em.set_author(name=f"{evType} Event", icon_url="https://i.imgur.com/7iWG4Rl.png")
                    elif 'Gold' in eventXY[3]:
                        em.set_author(name=f"{evType} Event", icon_url="https://i.imgur.com/oxuGOem.png")
                    elif 'Silver' in eventXY[3]:
                        em.set_author(name=f"{evType} Event", icon_url="https://i.imgur.com/CS3hGFX.png")
                    elif 'Bronze' in eventXY[3]:
                        em.set_author(name=f"{evType} Event", icon_url="https://i.imgur.com/47tb6qR.png")
                    else:
                        em.set_author(name=f"{evType} Event", icon_url="https://i.imgur.com/HlsskVP.png")
                elif evType == 'Team':
                    pass

                if evName in self.evInf.keys() and self.evInf[evName]['logo']:
                    em.set_thumbnail(url=self.evInf[evName]['logo'])
                else:
                    em.set_thumbnail(url=self.evInf['Other']['logo'])

                if (evType == 'General') and (eventXY[2] != None):
                    em.add_field(name="Region", value=eventXY[2], inline=True)
                elif (evType == 'Amateur') and (eventXY[3] != None):
                    em.add_field(name="League", value=eventXY[3], inline=True)

                if eventXY[4]:
                    em.add_field(name="Server", value=eventXY[4], inline=True)
                if eventXY[5]:
                    em.add_field(name="Prizepool", value=eventXY[5], inline=False)

                cfVal = None
                if eventXY[6]:
                    if any(char.isdigit() for char in eventXY[7]) == False and eventXY[7] == None and evName in self.evInf.keys():
                        codeNr = eventXY[0].split(' ')[-1].replace("#", "").replace(".", "")
                        eventXY[7] = self.evInf[evName]['code'].replace("$", str(codeNr))
                    cfVal = "[Matcherino]({}) - free $1 code `{}`".format(eventXY[6], eventXY[7])
                if evName in self.evInf.keys():
                    if self.evInf[evName]['patreon']:
                        if cfVal:
                            cfVal += "\n[Patreon]({}) - contribute to increase the prize pool".format(self.evInf[evName]['patreon'])
                        else:
                            cfVal = "[Patreon]({}) - contribute to increase the prize pool".format(self.evInf[evName]['patreon'])

                if cfVal:
                    em.add_field(name="Crowdfunding", value=cfVal, inline=False)

                if eventXY[8]:
                    em.add_field(name='▬▬▬▬▬▬▬', value='[**SIGN UP HERE**]({})'.format(eventXY[8]), inline=False)

                em.set_footer(text="Adjutant DiscordBot by Phoenix#2694", icon_url='https://avatars2.githubusercontent.com/u/36424912?s=60&v=4')

                if p:
                    await self.send_event(msg, em, srv, evType)
                elif not p:
                    await self.send_event_update(pMsg, msg, em)

            elif (-float(self.srvInf['general']['deleteDelay']) <= countdown <= 0) and not p:
                msg = f'{evType} Event already started.'
                await self.send_event_update(pMsg, msg, pMsg.embeds[0])

            elif (countdown < -float(self.srvInf['general']['deleteDelay'])) and not p:
                dEvCount += 1
                await self.del_old_events(pMsg)
        log.info(f'{pEvCount} / {aEvCount}  {evType} events already posted and {dEvCount} got deleted in {srv.name}')


    async def fetch_soups(self, url, eventTypes, parser):
        soups = [[], [], []]
        # Use a custom HTTP "User-Agent" header in your requests that identifies your project / use of the API, and includes contact information.
        headers = {'User-Agent': 'Adjutant-DiscordBot/1.5 (https://github.com/K4cePhoenix/Adjutant-DiscordBot; k4cephoenix@gmail.com)', 'Accept-Encoding': 'gzip'}
        async with aiohttp.ClientSession(headers=headers) as session:
            for ind, evt in enumerate(eventTypes):
                params = {'action': 'parse', 'format': 'json', 'page': f'User:(16thSq)_Kuro/{evt}_Tournaments', 'prop': 'text', 'formatversion': '2'}
                async with session.get(url, params=params) as response:
                    json_body = await response.json()
                    soups[ind] = BeautifulSoup(json_body['parse']['text'], parser)
                if ind != len(eventTypes)-1:
                    # Liquipedia API usage guideline: "action=parse" [...] requests should not exceed 1 request per 30 seconds [...].
                    await asyncio.sleep(30.1)
            return soups


    async def check_all_events(self):
        events = [[], [], []]
        eventTypes = ['Open', 'Amateur', 'Team']

        soups = await self.fetch_soups('http://liquipedia.net/starcraft2/api.php', eventTypes, 'html.parser')
        for ind, evt in enumerate(eventTypes):
            events[ind] = kuevst.steal(evt, soups[ind])

        log.info(f'Fetched {len(events[0])} general, {len(events[1])} amateur and {len(events[2])} team events')
        for guild in self.adjutant.guilds:
            msgs = []
            chan = []
            for x, evType in enumerate(['General', 'Amateur', 'Team']):
                log.info('processing {} events in {}'.format(evType, guild.name))
                for channel in guild.channels:
                    for srv in self.srvInf['guilds']:
                        if (guild.name == srv) and (channel.name == self.srvInf['guilds'][srv][f'channel_{evType}']) and channel.permissions_for(guild.me).read_messages:
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
