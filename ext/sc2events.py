from datetime import datetime, timedelta
from discord.ext import commands
import aiohttp
import aiosqlite
import asyncio
import discord
import logging
import pytz
import random
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


    @commands.command(name='upcoming')
    async def _upcoming(self, ctx):
        async with aiosqlite.connect('./data/db/adjutant.sqlite3') as db:
            try:
                sql = "SELECT * FROM events;"
                cursor = await db.execute(sql)
                tmp_data = await cursor.fetchall()
                await cursor.close()
                lUpdate = tmp_data[0][8]
            except Exception as e:
                log.debug(f'sc2events module command "upcoming" - {e}')
            gVal = ""
            aVal = ""
            for ind in range(10):
                if tmp_data[ind][8] != lUpdate:
                    pass
                elif ind <= 4:
                    gVal += f"{ind+1}. [**{tmp_data[ind][1]}**]({tmp_data[ind][6]}) in {tmp_data[ind][2]}\n"
                elif 5 <= ind <= 9:
                    aVal += f"{ind-4}. [**{tmp_data[ind][1]}**]({tmp_data[ind][6]}) in {tmp_data[ind][2]}\n"

            em = discord.Embed(title="Upcoming Events",
                               colour=discord.Colour(int(random.randint(0, 16777215))),
                               description=f"Last Update at {lUpdate}")
            em.add_field(name="Open Tournaments", value=gVal, inline=True)
            em.add_field(name="Amateur Tournaments", value=aVal, inline=True)
            em.set_footer(text="Information provided by Liquipedia, licensed under CC BY-SA 3.0 | https://liquipedia.net/",
                          icon_url='https://avatars2.githubusercontent.com/u/36424912?s=60&v=4')

            await ctx.send(embed=em)


    async def decrypt_evmessage(self, evMsg, evData, evType, emBool):
        key_words = [
            'name', 'region', 'server', 'league', 'prizepool',
            'hours', 'minutes', 'bracket', 'countdown', 'type'
        ]
        key_words_short = [
            'n', 'r', 's', 'l', 'pp',
            'h', 'min', 'grid', 'cd', 't'
        ]
        key_words_special = [
            'linebreak', 'newline', 'br'
        ]
        hours = evData['cd'].seconds // (60 * 60)
        mins = (evData['cd'].seconds-(hours * (60 * 60))) // 60
        cd = f"{hours}h {mins}min"

        evDataList = [
            evData['name'], evData['region'], evData['server'],
            evData['league'], evData['prize'], str(hours),
            str(mins), f"<{evData['bracket']}>", str(cd), evType
        ]
        evSpecialList = [
            '\n', '\n', '\n'
        ]

        for key_word_ind, key_word in enumerate(key_words):
            if f"${key_word}$" in evMsg:
                evMsg = evMsg.replace(f"${key_word}$", evDataList[key_word_ind])
            if not f"$" in evMsg:
                break
        for key_word_ind, key_word in enumerate(key_words_short):
            if f"${key_word}$" in evMsg:
                evMsg = evMsg.replace(f"${key_word}$", evDataList[key_word_ind])
            if not f"$" in evMsg:
                break
        for key_word_ind, key_word in enumerate(key_words_special):
            if f"${key_word}$" in evMsg:
                evMsg = evMsg.replace(f"${key_word}$", evSpecialList[key_word_ind])
            if not f"$" in evMsg:
                break

        if not emBool:
            evMsg = f"{evMsg}\n\nInformation provided by Liquipedia, licensed under CC BY-SA 3.0 | <https://liquipedia.net/>"

        return evMsg


    async def del_old_events(self, msg, countdown):
        try:
            await msg.delete()
            log.info(f'{msg.guild}, {msg.channel} - deleted {msg.embeds[0].title} - {countdown}')
        except Exception as e:
            log.error(f'{msg.guild}, {msg.channel} - MISSING PERMISSION - event deletion\n{e}')


    async def send_event_update(self, oldMsg, msg, em):
        try:
            await oldMsg.edit(content=msg, embed=em)
            log.info(f'{oldMsg.guild}, {oldMsg.channel} - updated {em.title}')
        except Exception as e:
            log.error(f'{oldMsg.guild}, {oldMsg.channel} - MISSING PERMISSION - can not update {em.title}\n{e}')


    async def send_event(self, msg, em, channel, evType):
        if channel.permissions_for(channel.guild.me).send_messages:
            await channel.send(msg, embed=em)


    async def post_events(self, eventsX, msgs, guild, channel, evType):
        aEvCount = 0
        pEvCount = 0
        dEvCount = 0

        for eventXY in eventsX:
            try:
                if eventXY['cd']:
                    countdown = (eventXY['cd'].days * 24) + (eventXY['cd'].seconds / (60 * 60))
                else:
                    countdown = -1.0
                p = True
                for MsgsEv in msgs:
                    if MsgsEv.embeds:
                        if eventXY['name'] == MsgsEv.embeds[0].title:
                            p = False
                            aEvCount += 1
                            pEvCount += 1
                            pMsg = MsgsEv
                            break
                    if any([eventXY['name'] in MsgsEv.content, eventXY['bracket'] in MsgsEv.content]):
                        p = False
                        aEvCount += 1
                        pEvCount += 1
                        pMsg = MsgsEv
                        break
                if 0 < countdown < float(self.bot.CONFIG['sc2oe']['countdown']):
                    aEvCount += 1
                    evName = ''.join(eventXY['name'].split(' ')[:len(eventXY['name'].split(' '))-1]).lower()
                    if guild[10] == 1:
                        timeform = eventXY['date24']
                    elif guild[10] == 0:
                        timeform = eventXY['date12']
                    else:
                        timeform = ''
                    if not timeform:
                        timeform = '???'
                    if evName in self.bot.evInf.keys() and self.bot.evInf[evName]['colour']:
                        try:
                            em = discord.Embed(title=eventXY['name'],
                                            colour=discord.Colour(int(self.bot.evInf[evName]['colour'], 16)),
                                            description=f"{timeform}")
                        except:
                            em = discord.Embed(title=eventXY['name'],
                                            colour=discord.Colour(int(self.bot.evInf[evName]['colour'], 16)),
                                            description="-")
                    else:
                        try:
                            em = discord.Embed(title=eventXY['name'],
                                            colour=discord.Colour(0x555555),
                                            description=f"{timeform}")
                        except:
                            em = discord.Embed(title=eventXY['name'],
                                            colour=discord.Colour(0x555555),
                                            description="-")

                    msg = await self.decrypt_evmessage(guild[11], eventXY, evType, channel.permissions_for(channel.guild.me).embed_links)
                    evTypeEmText = f"{evType} Event"
                    if evType == 'General':
                        em.set_author(name=evTypeEmText, icon_url=self.ICN_GRN)
                    elif evType == 'Amateur':
                        if 'Master' in eventXY['league']:
                            em.set_author(name=evTypeEmText, icon_url=self.ICN_MST)
                        elif 'Diamond' in eventXY['league']:
                            em.set_author(name=evTypeEmText, icon_url=self.ICN_DIA)
                        elif 'Platinum' in eventXY['league']:
                            em.set_author(name=evTypeEmText, icon_url=self.ICN_PLT)
                        elif 'Gold' in eventXY['league']:
                            em.set_author(name=evTypeEmText, icon_url=self.ICN_GLD)
                        elif 'Silver' in eventXY['league']:
                            em.set_author(name=evTypeEmText, icon_url=self.ICN_SLV)
                        elif 'Bronze' in eventXY['league']:
                            em.set_author(name=evTypeEmText, icon_url=self.ICN_BRN)
                        else:
                            em.set_author(name=evTypeEmText, icon_url=self.ICN_ALT)
                    elif evType == 'Team':
                        pass

                    if evName in self.bot.evInf.keys() and self.bot.evInf[evName]['logo']:
                        em.set_thumbnail(url=self.bot.evInf[evName]['logo'])
                    else:
                        em.set_thumbnail(url=self.bot.evInf['other']['logo'])

                    if evType == 'General' and eventXY['region']:
                        em.add_field(name="Region", value=eventXY['region'], inline=True)
                    elif evType == 'Amateur' and eventXY['league']:
                        em.add_field(name="League", value=eventXY['league'], inline=True)

                    if eventXY['server']:
                        em.add_field(name="Server", value=eventXY['server'], inline=True)
                    if eventXY['prize']:
                        em.add_field(name="Prizepool", value=eventXY['prize'], inline=False)

                    cfVal = ''
                    if eventXY['matLink']:
                        if (any(char.isdigit() for char in eventXY['matCode']) == False
                                and eventXY['matCode'] == ''
                                and evName in self.bot.evInf.keys()):
                            codeNr = eventXY['name'].split(' ')[-1].replace("#", "").replace(".", "")
                            eventXY['matCode'] = self.bot.evInf[evName]['code'].replace("$", str(codeNr))
                        cfVal = f"[Matcherino]({eventXY['matLink']}) - free $1 code `{eventXY['matCode']}`"
                    if evName in self.bot.evInf.keys():
                        if self.bot.evInf[evName]['patreon']:
                            if cfVal:
                                cfVal += f"\n[Patreon]({self.bot.evInf[evName]['patreon']}) - contribute to increase the prize pool"
                            else:
                                cfVal = f"[Patreon]({self.bot.evInf[evName]['patreon']}) - contribute to increase the prize pool"
                    if cfVal:
                        em.add_field(name="Crowdfunding", value=cfVal, inline=False)

                    if eventXY['bracket']:
                        em.add_field(name='▬▬▬▬▬▬▬', value=f"[**SIGN UP HERE**]({eventXY['bracket']})", inline=False)
                    em.set_footer(text="Information provided by Liquipedia, licensed under CC BY-SA 3.0 | https://liquipedia.net/",
                                icon_url='https://avatars2.githubusercontent.com/u/36424912?s=60&v=4')

                    if p:
                        data = guild[9]
                        if data:
                            data_list = data.split('$')
                            if len(data_list) == 1 and data_list[0] == '*':
                                await self.send_event(msg, em, channel, evType)
                            elif len(data_list) > 1:
                                for eventsItem in data_list[1:]:
                                    if eventsItem in eventXY['name']:
                                        await self.send_event(msg, em, channel, evType)
                            else:
                                pass
                    elif not p:
                        await self.send_event_update(pMsg, msg, em)

                elif (-float(self.bot.CONFIG['sc2oe']['deleteDelay']) <= countdown <= 0) and not p:
                    msg = f'{evType} event has started.'
                    await self.send_event_update(pMsg, msg, pMsg.embeds[0])

                elif (countdown < -float(self.bot.CONFIG['sc2oe']['deleteDelay'])) and not p:
                    dEvCount += 1
                    await self.del_old_events(pMsg, countdown)

            except Exception as e:
                    exc = f'{type(e).__name__}: {e}'
                    print(evType + ' failed to update.')
                    log.error(f'Failed to update {evType} - {exc}')

        log.info(f'{pEvCount} / {aEvCount}  {evType} events already posted and {dEvCount} got deleted in {channel.guild.name}')


    async def fetch_texts(self, eventTypes):
        # Use a custom HTTP "User-Agent" header in your requests that identifies your project / use of the API, and includes contact information.
        _URL = 'https://liquipedia.net/starcraft2/api.php'
        headers = {'User-Agent': f'{self.bot.FULL_NAME}/v{self.bot.VERSION} ({self.bot.GITHUB}; {self.bot.MAIL})',
                   'Accept-Encoding': 'gzip'}
        params = {
            'format': 'json',
            'formatversion': '2',
            'action': 'query',
            'titles': 'User:(16thSq)_Kuro/Open_Tournaments|User:(16thSq)_Kuro/Amateur_Tournaments|User:(16thSq)_Kuro/Team_Tournaments',
            'continue': '',
            'prop': 'revisions',
            'rvprop': 'content',
        }

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

        async with aiosqlite.connect('./data/db/adjutant.sqlite3') as db:
            sql = "SELECT * FROM guilds;"
            cursor = await db.execute(sql)
            guilds = await cursor.fetchall()
            await cursor.close()
        for guild in guilds:
            msgs = []
            for ind, evType in enumerate(eventTypes[:-1]):
                log.info(f'Processing {evType} Events in {guild[1]}')
                if guild[2*ind+2] != -1:
                    channel = self.bot.get_channel(guild[2*ind+2])
                    if channel.permissions_for(channel.guild.me).read_messages:
                        async for message in channel.history():
                            if message.author == channel.guild.me:
                                msgs.append(message)
                    else:
                        return
                    await self.post_events(events[ind], msgs, guild, channel, evType)

        lupd = f"{datetime.now(tz=pytz.utc)}"
        async with aiosqlite.connect('./data/db/adjutant.sqlite3') as db:
            for ind, evType in enumerate(eventTypes[:-1]):
                sorted_events = sorted(events[ind], key=lambda k: k['cd'])
                sorted_events_stripped = list()
                for sorted_event in sorted_events:
                    if int(sorted_event['cd'].days) >= 0:
                        sorted_events_stripped.append(sorted_event)
                eventNum = min(5, len(sorted_events_stripped))
                for ind2, sorted_event in enumerate(sorted_events_stripped[:eventNum]):
                    cd_h = sorted_event['cd'].seconds // (60 * 60)
                    cd_m = (sorted_event['cd'].seconds-(cd_h * (60 * 60))) // 60
                    if sorted_event['cd'].days:
                        cd = f"{sorted_event['cd'].days} days {cd_h}h {cd_m}min"
                    else:
                        cd = f"{cd_h}h {cd_m}min"
                    try:
                        sql = "UPDATE events SET name = ?, cd = ?, region = ?, server = ?, prizepool = ?, bracket = ?, type = ?, lastupdate = ? WHERE id = ?;"
                        await db.execute(sql, (sorted_event['name'], cd, sorted_event['region'], sorted_event['server'], sorted_event['prize'], sorted_event['bracket'], evType, lupd, ind*5+ind2,))
                    except:
                        await db.rollback()
                    finally:
                        await db.commit()




    async def check_events_in_background(self):
        await self.bot.wait_until_ready()
        self.bot.evInf = toml.load(self.bot.SC2DAT_PATH + self.bot.EVTINF_FILE)
        while True:
            await self.check_all_events()
            nextUpdateTime = datetime.now(tz=pytz.utc) + timedelta(minutes=float(self.bot.CONFIG['sc2oe']['sleepDelay']))
            log.info(f'Next event check at {nextUpdateTime:%b %d, %H:%M (%Z)}')
            await asyncio.sleep(float(self.bot.CONFIG['sc2oe']['sleepDelay']) * 60)


def setup(bot):
    n = SC2OpenEvents(bot)
    bot.add_cog(n)
    bot.loop.create_task(n.check_events_in_background())
