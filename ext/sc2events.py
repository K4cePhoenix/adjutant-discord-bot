from datetime import datetime, timedelta
from discord.ext import commands
import aiohttp
import aiosqlite
import asyncio
import discord
import logging
import pytz
import random

from .utils import kuevstv2


log = logging.getLogger('adjutant.sc2oe')


class SC2OpenEvents:
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
        self.LOGO_OTHER = "https://i.imgur.com/GJbwa0d.png"

    @commands.command(name='upcoming', aliases=['next'])
    async def _upcoming(self, ctx):
        async with aiosqlite.connect('./data/db/adjutant.sqlite3') as db:
            try:
                sql = "SELECT * FROM events;"
                cursor = await db.execute(sql)
                all_rows = await cursor.fetchall()
                await cursor.close()
                last_update = all_rows[0][8]
                general_tournament_info_str = ""
                amateur_tournament_info_str = ""
                time_since_last_update = datetime.now(tz=pytz.utc) - datetime.strptime(last_update[:-3]+"00", "%Y-%m-%d %H:%M:%S.%f%z")
                for ind, tmp_data in enumerate(all_rows):
                    if len(tmp_data[2].split(' ')) == 4:
                        saved_cd_time = int(tmp_data[2].split(' ')[0]) * 24 * 60 * 60
                        saved_cd_time += int(tmp_data[2].split(' ')[2][:-1]) * 60 * 60
                        saved_cd_time += int(tmp_data[2].split(' ')[3][:-3]) * 60
                    elif len(tmp_data[2].split(' ')) == 2:
                        saved_cd_time = int(tmp_data[2].split(' ')[0][:-1]) * 60 * 60
                        saved_cd_time += int(tmp_data[2].split(' ')[1][:-3]) * 60
                    elif len(tmp_data[2].split(' ')) == 1:
                        saved_cd_time = int(tmp_data[2].split(' ')[0][:-3]) * 60
                    else:
                        saved_cd_time = 0
                    cur_t = saved_cd_time - time_since_last_update.total_seconds()

                    if cur_t > 0:
                        d = int(cur_t // (60 * 60 * 24))
                        h = int((cur_t-(d * (60 * 60 * 24))) // (60 * 60))
                        m = int((cur_t-(d * (60 * 60 * 24) + h * (60 * 60))) // 60)
                        if d:
                            if tmp_data[8] != last_update:
                                pass
                            elif ind <= 4:
                                general_tournament_info_str += f"{ind+1}. [**{tmp_data[1]}**]({tmp_data[6]}) in {d} days {h}h {m}min\n"
                            elif 5 <= ind <= 9:
                                amateur_tournament_info_str += f"{ind-4}. [**{tmp_data[1]}**]({tmp_data[6]}) in {d} days {h}h {m}min\n"
                        elif h:
                            if tmp_data[8] != last_update:
                                pass
                            elif ind <= 4:
                                general_tournament_info_str += f"{ind+1}. [**{tmp_data[1]}**]({tmp_data[6]}) in {h}h {m}min\n"
                            elif 5 <= ind <= 9:
                                amateur_tournament_info_str += f"{ind-4}. [**{tmp_data[1]}**]({tmp_data[6]}) in {h}h {m}min\n"
                        else:
                            if tmp_data[8] != last_update:
                                pass
                            elif ind <= 4:
                                general_tournament_info_str += f"{ind+1}. [**{tmp_data[1]}**]({tmp_data[6]}) in {m}min\n"
                            elif 5 <= ind <= 9:
                                amateur_tournament_info_str += f"{ind-4}. [**{tmp_data[1]}**]({tmp_data[6]}) in {m}min\n"

                em = discord.Embed(title="Upcoming Events",
                                   colour=discord.Colour(int(random.randint(0, 16777215))),
                                   description=f"Last Update at {last_update}")
                em.add_field(name="Open Tournaments", value=general_tournament_info_str, inline=True)
                em.add_field(name="Amateur Tournaments", value=amateur_tournament_info_str, inline=True)
                em.set_footer(text="Information provided by Liquipedia, licensed under CC BY-SA 3.0 | https://liquipedia.net/",
                              icon_url='https://avatars2.githubusercontent.com/u/36424912?s=60&v=4')

                await ctx.send(embed=em)
            except Exception as e:
                log.debug(f'sc2events module command "upcoming" - {e}')

    @staticmethod
    async def decrypt_event_message(event_msg, event_data, event_type, is_embed):
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
        hours = event_data['cd'].seconds // (60 * 60)
        mins = (event_data['cd'].seconds-(hours * (60 * 60))) // 60
        cd = f"{hours}h {mins}min"

        event_data_list = [
            event_data['name'], event_data['region'], event_data['server'],
            event_data['league'], event_data['prize'], str(hours),
            str(mins), f"<{event_data['bracket']}>", str(cd), event_type
        ]
        event_special_list = [
            '\n', '\n', '\n'
        ]

        for key_word_ind, key_word in enumerate(key_words):
            if f"${key_word}$" in event_msg:
                event_msg = event_msg.replace(f"${key_word}$", event_data_list[key_word_ind])
            if f"$" not in event_msg:
                break
        for key_word_ind, key_word in enumerate(key_words_short):
            if f"${key_word}$" in event_msg:
                event_msg = event_msg.replace(f"${key_word}$", event_data_list[key_word_ind])
            if f"$" not in event_msg:
                break
        for key_word_ind, key_word in enumerate(key_words_special):
            if f"${key_word}$" in event_msg:
                event_msg = event_msg.replace(f"${key_word}$", event_special_list[key_word_ind])
            if f"$" not in event_msg:
                break

        if not is_embed:
            event_msg = f"{event_msg}\n\nInformation provided by Liquipedia, licensed under CC BY-SA 3.0 | <https://liquipedia.net/>"

        return event_msg

    @staticmethod
    async def del_old_events(msg, countdown):
        try:
            await msg.delete()
            log.info(f'{msg.guild}, {msg.channel} - deleted {msg.embeds[0].title} - {countdown}')
        except Exception as e:
            log.error(f'{msg.guild}, {msg.channel} - MISSING PERMISSION - event deletion\n{e}')

    @staticmethod
    async def send_event_update(old_msg, msg, em):
        try:
            await old_msg.edit(content=msg, embed=em)
            log.info(f'{old_msg.guild}, {old_msg.channel} - updated {em.title}')
        except Exception as e:
            log.error(f'{old_msg.guild}, {old_msg.channel} - MISSING PERMISSION - can not update {em.title}\n{e}')

    @staticmethod
    async def send_event(msg, em, channel):
        if channel.permissions_for(channel.guild.me).send_messages:
            await channel.send(msg, embed=em)

    async def post_events(self, events_x, msgs, guild, channel, event_type):
        all_event_counter = 0
        posted_event_counter = 0
        deleted_event_counter = 0

        for event_xy in events_x:
            try:
                if event_xy['cd']:
                    countdown = (event_xy['cd'].days * 24) + (event_xy['cd'].seconds / (60 * 60))
                else:
                    countdown = -1.0
                p = True
                for MsgsEv in msgs:
                    if MsgsEv.embeds:
                        if event_xy['name'] == MsgsEv.embeds[0].title:
                            p = False
                            all_event_counter += 1
                            posted_event_counter += 1
                            posted_msg = MsgsEv
                            break
                    if any([event_xy['name'] in MsgsEv.content, event_xy['bracket'] in MsgsEv.content]):
                        p = False
                        all_event_counter += 1
                        posted_event_counter += 1
                        posted_msg = MsgsEv
                        break
                if 0 < countdown < float(self.bot.CONFIG['sc2oe']['countdown']):
                    all_event_counter += 1
                    event_name = ''.join(event_xy['name'].split(' ')[:len(event_xy['name'].split(' '))-1]).lower()
                    if guild[10] == 1:
                        time_format = event_xy['date24']
                    elif guild[10] == 0:
                        time_format = event_xy['date12']
                    else:
                        time_format = ''
                    if event_name in self.event_info.keys() and self.event_info[event_name]['colour']:
                        if time_format:
                            em = discord.Embed(title=event_xy['name'],
                                               colour=discord.Colour(int(self.event_info[event_name]['colour'], 16)),
                                               description=f"{time_format}")
                        else:
                            em = discord.Embed(title=event_xy['name'],
                                               colour=discord.Colour(int(self.event_info[event_name]['colour'], 16)),
                                               description="-")
                    else:
                        if time_format:
                            em = discord.Embed(title=event_xy['name'],
                                               colour=discord.Colour(0x555555),
                                               description=f"{time_format}")
                        else:
                            em = discord.Embed(title=event_xy['name'],
                                               colour=discord.Colour(0x555555),
                                               description="-")

                    msg = await self.decrypt_event_message(guild[11], event_xy, event_type, channel.permissions_for(channel.guild.me).embed_links)
                    event_type_embed_txt = f"{event_type} Event"
                    if event_type == 'General':
                        em.set_author(name=event_type_embed_txt, icon_url=self.ICN_GRN)
                    elif event_type == 'Amateur':
                        if 'Master' in event_xy['league']:
                            em.set_author(name=event_type_embed_txt, icon_url=self.ICN_MST)
                        elif 'Diamond' in event_xy['league']:
                            em.set_author(name=event_type_embed_txt, icon_url=self.ICN_DIA)
                        elif 'Platinum' in event_xy['league']:
                            em.set_author(name=event_type_embed_txt, icon_url=self.ICN_PLT)
                        elif 'Gold' in event_xy['league']:
                            em.set_author(name=event_type_embed_txt, icon_url=self.ICN_GLD)
                        elif 'Silver' in event_xy['league']:
                            em.set_author(name=event_type_embed_txt, icon_url=self.ICN_SLV)
                        elif 'Bronze' in event_xy['league']:
                            em.set_author(name=event_type_embed_txt, icon_url=self.ICN_BRN)
                        else:
                            em.set_author(name=event_type_embed_txt, icon_url=self.ICN_ALT)
                    elif event_type == 'Team':
                        pass

                    if event_name in self.event_info.keys() and self.event_info[event_name]['logo']:
                        em.set_thumbnail(url=self.event_info[event_name]['logo'])
                    else:
                        em.set_thumbnail(url=self.LOGO_OTHER)

                    if event_type == 'General' and event_xy['region']:
                        em.add_field(name="Region", value=event_xy['region'], inline=True)
                    elif event_type == 'Amateur' and event_xy['league']:
                        em.add_field(name="League", value=event_xy['league'], inline=True)

                    if event_xy['server']:
                        em.add_field(name="Server", value=event_xy['server'], inline=True)
                    if event_xy['prize']:
                        em.add_field(name="Prizepool", value=event_xy['prize'], inline=False)

                    crowdfunding_str = ''
                    if event_xy['matLink']:
                        crowdfunding_str = f"[Matcherino]({event_xy['matLink']})"
                        if (any(char.isdigit() for char in event_xy['matCode']) is False
                                and event_xy['matCode'] == ''
                                and event_name in self.event_info.keys()):
                            code_num = event_xy['name'].split(' ')[-1].replace("#", "").replace(".", "")
                            event_xy['matCode'] = self.event_info[event_name]['code'].replace("$", str(code_num))
                        if event_xy['matCode']:
                            crowdfunding_str += f" - free $1 code `{event_xy['matCode']}`"
                    if event_name in self.event_info.keys():
                        if self.event_info[event_name]['patreon']:
                            if crowdfunding_str:
                                crowdfunding_str += f"\n[Patreon]({self.event_info[event_name]['patreon']}) - contribute to increase the prize pool"
                            else:
                                crowdfunding_str = f"[Patreon]({self.event_info[event_name]['patreon']}) - contribute to increase the prize pool"
                    if crowdfunding_str:
                        em.add_field(name="Crowdfunding", value=crowdfunding_str, inline=False)

                    if event_xy['bracket']:
                        em.add_field(name='▬▬▬▬▬▬▬', value=f"[**SIGN UP HERE**]({event_xy['bracket']})", inline=False)
                    em.set_footer(text="Information provided by Liquipedia, licensed under CC BY-SA 3.0 | https://liquipedia.net/",
                                  icon_url='https://avatars2.githubusercontent.com/u/36424912?s=60&v=4')

                    if p:
                        data = guild[9]
                        if data:
                            data_list = data.split('$')
                            if len(data_list) == 1 and data_list[0] == '*':
                                await self.send_event(msg, em, channel)
                            elif len(data_list) > 1:
                                for eventsItem in data_list[1:]:
                                    if eventsItem in event_xy['name']:
                                        await self.send_event(msg, em, channel)
                            else:
                                pass
                    elif not p:
                        await self.send_event_update(posted_msg, msg, em)

                elif (-float(self.bot.CONFIG['sc2oe']['deleteDelay']) <= countdown <= 0) and not p:
                    msg = f'{event_type} event has started.'
                    await self.send_event_update(posted_msg, msg, posted_msg.embeds[0])

                elif (countdown < -float(self.bot.CONFIG['sc2oe']['deleteDelay'])) and not p:
                    deleted_event_counter += 1
                    await self.del_old_events(posted_msg, countdown)

            except Exception as e:
                    exc = f"{type(e).__name__}: {e}"
                    print(event_type + ' failed to update.')
                    log.error(f'Failed to update {event_type} - {exc}')
        log.info(f"{posted_event_counter} / {all_event_counter}  {event_type} events already posted and {deleted_event_counter} got deleted in {channel.guild.name}")

    async def fetch_texts(self, event_types):
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
        event_text = dict()
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(_URL, params=params) as response:
                json_body = await response.json()
                for ind, event_type in enumerate(event_types):
                    event_text[event_type] = json_body['query']['pages'][ind]['revisions'][0]['content']
        return event_text

    async def check_all_events(self):
        event_types = ['General', 'Amateur', 'Team']
        txts = await self.fetch_texts(event_types)
        events = kuevstv2.steal(txts)
        log.info(f'Fetched {len(events[0])} general, {len(events[1])} amateur and {len(events[2])} team events')

        async with aiosqlite.connect('./data/db/adjutant.sqlite3') as db:
            sql = "SELECT * FROM guilds;"
            cursor = await db.execute(sql)
            guilds = await cursor.fetchall()
            await cursor.close()
        for guild in guilds:
            msgs = []
            for ind, event_type in enumerate(event_types[:-1]):
                log.info(f'Processing {event_type} Events in {guild[1]}')
                if guild[2*ind+2] != -1:
                    channel = self.bot.get_channel(guild[2*ind+2])
                    if channel.permissions_for(channel.guild.me).read_messages:
                        async for message in channel.history():
                            if message.author == channel.guild.me:
                                msgs.append(message)
                    else:
                        return
                    await self.post_events(events[ind], msgs, guild, channel, event_type)

        updated_at = f"{datetime.now(tz=pytz.utc)}"
        async with aiosqlite.connect('./data/db/adjutant.sqlite3') as db:
            for ind, event_type in enumerate(event_types[:-1]):
                sorted_events = sorted(events[ind], key=lambda k: k['cd'])
                events_stripped = list()
                for event in sorted_events:
                    if int(event['cd'].days) >= 0:
                        events_stripped.append(event)
                event_num = min(5, len(events_stripped))
                for ind2, event in enumerate(events_stripped[:event_num]):
                    countdown_hours = event['cd'].seconds // (60 * 60)
                    countdown_mins = (event['cd'].seconds-(countdown_hours * (60 * 60))) // 60
                    if event['cd'].days:
                        cd = f"{event['cd'].days} days {countdown_hours}h {countdown_mins}min"
                    elif countdown_hours:
                        cd = f"{countdown_hours}h {countdown_mins}min"
                    else:
                        cd = f"{countdown_mins}min"
                    try:
                        sql = "UPDATE events SET name = ?, cd = ?, region = ?, server = ?, prizepool = ?, bracket = ?, type = ?, lastupdate = ? WHERE id = ?;"
                        await db.execute(sql, (event['name'], cd, event['region'], event['server'], event['prize'], event['bracket'], event_type, updated_at, ind*5+ind2,))
                    except Exception as e:
                        await db.rollback()
                        log.error(f"{type(e).__name__}: {e}")
                    finally:
                        await db.commit()

    async def check_events_in_background(self):
        await self.bot.wait_until_ready()
        async with aiosqlite.connect('./data/db/adjutant.sqlite3') as db:
            sql = "SELECT * FROM isocup_info"
            cursor = await db.execute(sql)
            isocup_info_list = await cursor.fetchall()
            await cursor.close()
        self.event_info = dict()
        for isocup in isocup_info_list:
            tmp_dict = {
                'name': isocup[1],
                'code': isocup[2],
                'org': isocup[3],
                'logo': isocup[4],
                'patreon': isocup[5],
                'colour': isocup[6]
            }
            ev_inf_name = ''.join(isocup[1].split(' ')).lower()
            self.event_info[ev_inf_name] = tmp_dict
        while True:
            await self.check_all_events()
            next_update_time = datetime.now(tz=pytz.utc) + timedelta(minutes=float(self.bot.CONFIG['sc2oe']['sleepDelay']))
            log.info(f"Next event check at {next_update_time:%b %d, %H:%M (%Z)}")
            await asyncio.sleep(float(self.bot.CONFIG['sc2oe']['sleepDelay']) * 60)


def setup(bot):
    n = SC2OpenEvents(bot)
    bot.add_cog(n)
    bot.loop.create_task(n.check_events_in_background())
