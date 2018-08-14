from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import aiofiles
import aiohttp
import asyncio
import discord
import feedparser
import logging
import os
import pytz
import time
import toml
import traceback


log = logging.getLogger('adjutant.rss')


class RSS():
    def __init__(self, bot):
        self.bot = bot
        self.data_path = './data/rss/'
        self.feeds_file = 'feeds.toml'
        if os.path.isdir(self.data_path) is False:
            os.makedirs(self.data_path)
        if os.path.isfile(self.data_path + self.feeds_file) is False:
            open(self.data_path+self.feeds_file, 'a').close()
        self.feeds = toml.load(self.data_path + self.feeds_file)


    async def fetch_feed(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                raw_feed = await response.text()
                return feedparser.parse(raw_feed)


    async def read_feeds_in_background(self):
        await self.bot.wait_until_ready()
        while True:
            self.feeds = toml.load(self.data_path + self.feeds_file)
            for feed in self.feeds['feeds']:
                log.info(f'RSS check: {feed}')
                feed_data = await self.fetch_feed(self.feeds['feeds'][feed]['feedURL'])
                for key in range(len(feed_data['entries'])-(len(feed_data['entries'])-2), -1, -1):
                    msg = f"{self.feeds['feeds'][feed]['name']}: {feed_data['entries'][key]['title']}"
                    em = discord.Embed(title=feed_data['entries'][key]['title'], colour=discord.Colour(int(self.feeds['feeds'][feed]['colour'], 16)), description=BeautifulSoup(feed_data['entries'][key]['summary'], 'html.parser').text.rstrip('More'))
                    em.set_author(name=self.feeds['feeds'][feed]['name'], icon_url=self.feeds['feeds'][feed]['icon'])
                    em.add_field(name='\u200b', value=f"[**READ MORE**]({self.feeds['feeds'][feed]['blogURL']}{feed_data['entries'][key]['id'].split('/')[-1]})", inline=False)
                    em.set_footer(text=f"Published at {time.strftime('%b %d, %H:%M', feed_data['entries'][key]['published_parsed'])} UTC")
                    log.info(f'{msg}')
                    for fSrv in self.feeds['servers']:
                        fChan = self.feeds['servers'][fSrv]['channel']
                        for guild in self.bot.guilds:
                            for channel in guild.channels:
                                if (guild.name == fSrv) and (channel.name == fChan) and not feed_data['entries'][key]['id'].split('/')[-1] in self.feeds['servers'][guild.name][f'ids_{feed}'] and channel.permissions_for(guild.me).send_messages:
                                    await channel.send(msg, embed=em)
                                    self.feeds['servers'][guild.name][f'ids_{feed}'].append(feed_data['entries'][key]['id'].split('/')[-1])
                                    # f = open(self.data_path+self.feeds_file, 'w')
                                    # toml.dump(self.feeds, f)
                                    # f.close()
                                    try:
                                        tomlStr = toml.dumps(self.feeds)
                                        async with aiofiles.open(self.data_path+self.feeds_file, 'w') as f:
                                            await f.write(tomlStr)
                                    except Exception:
                                        log.error("on_guild_join: Couldn't save server info file.")
                                        traceback.print_exc()
                                        pass
            nextUpdateTime = datetime.now(tz=pytz.utc) + timedelta(minutes=float(self.feeds['general']['sleepDelay']))
            log.info(f'Next rss feed check at {nextUpdateTime:%b %d, %H:%M (%Z)}')
            await asyncio.sleep(float(self.feeds['general']['sleepDelay']) * 60)


def setup(bot):
    n = RSS(bot)
    bot.add_cog(n)
    bot.loop.create_task(n.read_feeds_in_background())
