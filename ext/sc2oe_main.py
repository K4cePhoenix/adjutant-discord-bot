from datetime import datetime, timedelta
import aiohttp
import asyncio
import discord
import logging
import os
import pytz
import toml

from .sc2 import kuevstv2

log = logging.getLogger('adjutant.sc2oe')


class SC2OpenEvents():
    def __init__(self, bot):
        self.bot = bot
        self.ICN_GRN = "https://i.imgur.com/lTur4HM.png"
        self.ICN_MST = "https://i.imgur.com/R3M8AlH.png"
        self.ICN_DIA = "https://i.imgur.com/i3ceEMq.png"
        self.ICN_PLT = "https://i.imgur.com/7iWG4Rl.png"
        self.ICN_GLD = "https://i.imgur.com/oxuGOem.png"
        self.ICN_SLV = "https://i.imgur.com/CS3hGFX.png"
        self.ICN_BRN = "https://i.imgur.com/47tb6qR.png"
        self.ICN_ALT = "https://i.imgur.com/HlsskVP.png"

    async def del_old_events(self, msg, countdown):
        try:
            await msg.delete()
            log.info(f'{msg.guild}, {msg.channel} - deleted {msg.embeds[0].title} - {countdown}')
        except:
            log.error(f'{msg.guild}, {msg.channel} - MISSING PERMISSION - event deletion')

    async def send_event_update(self, oldMsg, msg, em):
        try:
            await oldMsg.edit(content=msg, embed=em)
            log.info(f'{oldMsg.guild}, {oldMsg.channel} - updated {em.title}')
        except:
            log.error(f'{oldMsg.guild}, {oldMsg.channel} - MISSING PERMISSION - can not update {em.title}')

    async def send_event(self, msg, em, srv, evType):
        for channel in srv.channels:
            for s in self.bot.srvInf['guilds']:
                ############# IDS INSTEAD OF NAMES #############
                # smth like
                # if srv.id == self.bot.srvInf['guilds'][s]['id']:
                
                #     ch = self.bot.get_channel(srv.id)
                #     if ch.permissions_for(srv.me):
                #         ch.send(msg, embed=em)
                #         log.info(f'{srv.name}/{srv.id}, {ch} - sent {em.title}')
                #         return
                if (srv.name == self.bot.srvInf['guilds'][s]['name'] 
                        and channel.name == self.bot.srvInf['guilds'][s][f'channel_{evType.lower()}'] 
                        and channel.permissions_for(srv.me).send_messages):
                    await channel.send(msg, embed=em)
                    log.info(f'{srv}, {channel} - sent {em.title}')
                    return

    async def post_events(self, eventsX, msgs, srv, evType):
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
            if 0 < countdown < float(self.bot.srvInf['general']['countdown']):
                aEvCount += 1
                cd_hours = eventXY[9].seconds // (60 * 60)
                cd_minutes = (eventXY[9].seconds-(cd_hours * (60 * 60))) // 60
                evName = ''.join(eventXY[0].split(' ')[:len(eventXY[0].split(' '))-1]).lower()
                if evName in self.bot.evInf.keys() and self.bot.evInf[evName]['colour']:
                    em = discord.Embed(title=eventXY[0],
                                       colour=discord.Colour(int(self.bot.evInf[evName]['colour'], 16)),
                                       description=f"{eventXY[1]}")
                else:
                    em = discord.Embed(title=eventXY[0],
                                       colour=discord.Colour(0x555555),
                                       description=f"{eventXY[1]}")

                msg = f'{evType} event is happening in {cd_hours}h {cd_minutes}min'
                if evType == 'General':
                    em.set_author(name=f"{evType} Event", icon_url=self.ICN_GRN)
                elif evType == 'Amateur':
                    if 'Master' in eventXY[3]:
                        em.set_author(name=f"{evType} Event", icon_url=self.ICN_MST)
                    elif 'Diamond' in eventXY[3]:
                        em.set_author(name=f"{evType} Event", icon_url=self.ICN_DIA)
                    elif 'Platinum' in eventXY[3]:
                        em.set_author(name=f"{evType} Event", icon_url=self.ICN_PLT)
                    elif 'Gold' in eventXY[3]:
                        em.set_author(name=f"{evType} Event", icon_url=self.ICN_GLD)
                    elif 'Silver' in eventXY[3]:
                        em.set_author(name=f"{evType} Event", icon_url=self.ICN_SLV)
                    elif 'Bronze' in eventXY[3]:
                        em.set_author(name=f"{evType} Event", icon_url=self.ICN_BRN)
                    else:
                        em.set_author(name=f"{evType} Event", icon_url=self.ICN_ALT)
                elif evType == 'Team':
                    pass

                if evName in self.bot.evInf.keys() and self.bot.evInf[evName]['logo']:
                    em.set_thumbnail(url=self.bot.evInf[evName]['logo'])
                else:
                    em.set_thumbnail(url=self.bot.evInf['other']['logo'])

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
                    if (any(char.isdigit() for char in eventXY[7]) == False 
                            and eventXY[7] == '' 
                            and evName in self.bot.evInf.keys()):
                        codeNr = eventXY[0].split(' ')[-1].replace("#", "").replace(".", "")
                        eventXY[7] = self.bot.evInf[evName]['code'].replace("$", str(codeNr))
                    cfVal = f"[Matcherino]({eventXY[6]}) - free $1 code `{eventXY[7]}`"
                if evName in self.bot.evInf.keys():
                    if self.bot.evInf[evName]['patreon']:
                        if cfVal:
                            cfVal += f"\n[Patreon]({self.bot.evInf[evName]['patreon']}) - contribute to increase the prize pool"
                        else:
                            cfVal = f"[Patreon]({self.bot.evInf[evName]['patreon']}) - contribute to increase the prize pool"
                if cfVal:
                    em.add_field(name="Crowdfunding", value=cfVal, inline=False)

                if eventXY[8]:
                    em.add_field(name='▬▬▬▬▬▬▬', value=f'[**SIGN UP HERE**]({eventXY[8]})', inline=False)
                em.set_footer(text="Information provided by Liquipedia, licensed under CC BY-SA 3.0 | https://liquipedia.net/", 
                              icon_url='https://avatars2.githubusercontent.com/u/36424912?s=60&v=4')

                if p:
                    await self.send_event(msg, em, srv, evType)
                elif not p:
                    await self.send_event_update(pMsg, msg, em)

            elif (-float(self.bot.srvInf['general']['deleteDelay']) <= countdown <= 0) and not p:
                msg = f'{evType} event has started.'
                await self.send_event_update(pMsg, msg, pMsg.embeds[0])

            elif (countdown < -float(self.bot.srvInf['general']['deleteDelay'])) and not p:
                dEvCount += 1
                await self.del_old_events(pMsg, countdown)

        # for MsgsEv in msgs:
        #     p2 = True
        #     for eventXY in eventsX:
        #         if MsgsEv.embeds:
        #             if eventXY[0] == MsgsEv.embeds[0].title:
        #                 p2 = False
        #                 break
        #     if p2 == True:
        #         dEvCount += 1
        #         await self.del_old_events(MsgsEv, -1.0)
        log.info(f'{pEvCount} / {aEvCount}  {evType} events already posted and {dEvCount} got deleted in {srv.name}')

    async def fetch_texts(self, eventTypes):
        # Use a custom HTTP "User-Agent" header in your requests that identifies your project / use of the API, and includes contact information.
        _URL = 'http://liquipedia.net/starcraft2/api.php'
        headers = {'User-Agent': f'Adjutant-DiscordBot/v{self.bot.VERSION} (https://github.com/K4cePhoenix/Adjutant-DiscordBot; k4cephoenix@gmail.com)', 
                   'Accept-Encoding': 'gzip'}
        params = dict()
        params['action'] = 'query'
        params['format'] = 'json'
        params['titles'] = 'User:(16thSq)_Kuro/Open_Tournaments|User:(16thSq)_Kuro/Amateur_Tournaments|User:(16thSq)_Kuro/Team_Tournaments'
        params['continue'] = ''
        params['prop'] = 'revisions'
        params['rvprop'] = 'content'
        params['formatversion'] = '2'
        evText = dict()
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(_URL, params=params) as response:
                json_body = await response.json()
                for ind, evType in enumerate(eventTypes):
                    evText[evType] = json_body['query']['pages'][ind]['revisions'][0]['content']
        return evText

    async def check_all_events(self):
        eventTypes = ['General', 'Amateur', 'Team']
        txts = await self.fetch_texts(eventTypes)
        events = kuevstv2.steal(txts)
        log.info(f'Fetched {len(events[0])} general, {len(events[1])} amateur and {len(events[2])} team events')
        for guild in self.bot.guilds:
            msgs = []
            for x, evType in enumerate(eventTypes):
                log.info(f'processing {evType} events in {guild.name}')
                for channel in guild.channels:
                    for srv in self.bot.srvInf['guilds']:
                        ############# IDS INSTEAD OF NAMES #############
                        if (guild.name == srv 
                                and channel.name == self.bot.srvInf['guilds'][srv][f'channel_{evType.lower()}'] 
                                and channel.permissions_for(guild.me).read_messages):
                            async for message in channel.history():
                                msgs.append(message)
                await self.post_events(events[x], msgs, guild, evType)

    async def check_events_in_background(self):
        await self.bot.wait_until_ready()
        while True:
            self.bot.evInf = toml.load(self.bot.SC2DAT_PATH + self.bot.EVTINF_FILE)
            self.bot.srvInf = toml.load(self.bot.SC2DAT_PATH + self.bot.SRVINF_FILE)
            await self.check_all_events()
            nextUpdateTime = datetime.now(tz=pytz.utc) + timedelta(minutes=float(self.bot.srvInf['general']['sleepDelay']))
            log.info(f'Next event check at {nextUpdateTime:%b %d, %H:%M (%Z)}')
            await asyncio.sleep(float(self.bot.srvInf['general']['sleepDelay']) * 60)


def setup(bot):
    n = SC2OpenEvents(bot)
    bot.add_cog(n)
    bot.loop.create_task(n.check_events_in_background())
