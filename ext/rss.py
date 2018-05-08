from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import aiohttp
import asyncio
import discord
import feedparser
import logging
import os
import pytz
import time
import toml

from .utils.chat_formatting import *


log = logging.getLogger('adjutant.rss')


class RSS():
    def __init__(self, adjutant):
        self.adjutant = adjutant
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
        await self.adjutant.wait_until_ready()
        while True:
            self.feeds = toml.load(self.data_path + self.feeds_file)
            for feed in self.feeds['feeds']:
                feed_data = await self.fetch_feed(self.feeds['feeds'][feed]['feedURL'])
                for key in range(len(feed_data['entries'])-(len(feed_data['entries'])-2), -1, -1):
                    msg = "{}: {}".format(self.feeds['feeds'][feed]['name'], feed_data['entries'][key]['title'])
                    em = discord.Embed(title=feed_data['entries'][key]['title'], colour=discord.Colour(int(self.feeds['feeds'][feed]['colour'], 16)), description=BeautifulSoup(feed_data['entries'][key]['summary'], 'html.parser').text.rstrip('More'))
                    em.set_author(name=self.feeds['feeds'][feed]['name'], icon_url=self.feeds['feeds'][feed]['icon'])
                    em.add_field(name='\u200b', value='[**READ MORE**]({}{})'.format(self.feeds['feeds'][feed]['blogURL'], feed_data['entries'][key]['id'].split('/')[-1]), inline=False)
                    em.set_footer(text="Published at {} UTC".format(time.strftime('%b %d, %H:%M', feed_data['entries'][key]['published_parsed'])))
                    for fSrv in self.feeds['general']['servers']:
                        for fChan in self.feeds['general']['channels']:
                            for guild in self.adjutant.guilds:
                                for channel in guild.channels:
                                    if (guild.name == fSrv) and (channel.name == fChan) and not feed_data['entries'][key]['id'].split('/')[-1] in self.feeds['feeds'][feed][guild.name]['ids'] and channel.permissions_for(guild.me).send_messages:
                                        await channel.send(msg, embed=em)
                                        self.feeds['feeds'][feed][guild.name]['ids'].append(feed_data['entries'][key]['id'].split('/')[-1])
                                        f = open(self.data_path+self.feeds_file, 'w')
                                        toml.dump(self.feeds, f)
                                        f.close()
            nextUpdateTime = datetime.now(tz=pytz.utc) + timedelta(hours=float(self.feeds['general']['sleepDelay']))
            log.info('Next event check at {:%b %d, %H:%M (%Z)}'.format(nextUpdateTime))
            await asyncio.sleep(float(self.feeds['general']['sleepDelay']) * 60)

def setup(adjutant):
    n = RSS(adjutant)
    adjutant.add_cog(n)
    adjutant.loop.create_task(n.read_feeds_in_background())
