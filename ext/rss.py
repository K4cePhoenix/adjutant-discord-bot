from discord.ext import commands
import aiohttp
import asyncio
import discord
import feedparser
import logging
import os
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
        self.session = aiohttp.ClientSession()

    async def get_current_feed(self, url):
        text = None
        try:
            with aiohttp.ClientSession() as session:
                with aiohttp.Timeout(3):
                    async with session.get(url) as r:
                        text = await r.text()
        except:
            pass
        return text


    async def read_feeds_in_background(self):
        await self.adjutant.wait_until_ready()
        while True:
            self.feeds = toml.load(self.data_path + self.feeds_file)
            for server in self.feeds['general']['servers']:
                for channel in self.feeds['general']['channels']:
                    for url in self.feeds['feeds']:
                        log.debug("checking {} on sid {}".format(url, server))
                        if channel is None:
                            log.debug("response channel not found, continuing")
                            continue
                        msg = await self.get_current_feed(url)
                        if msg is not None:
                            for srv in self.adjutant.guilds:
                                for srvCh in guild.channels:
                                    if (channel == srvCh.name) and (server == srv.name):
                                        await channel.send(msg)
            await asyncio.sleep(600)


def setup(adjutant):
    n = RSS(adjutant)
    adjutant.add_cog(n)
    adjutant.loop.create_task(n.read_feeds_in_background())
