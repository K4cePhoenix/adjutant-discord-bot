from discord.ext import commands
from bs4 import BeautifulSoup
import aiohttp
import asyncio
import discord

class Challonge():
    def __init__(self, bot):
        self.bot = bot
        self.API_KEY = self.bot.CONFIG['api']['challonge_token']
        self.USERNAME = self.bot.CONFIG['api']['challonge_uname']

    async def fetch_tour(self, tourId):
        _URL = f'https://{self.USERNAME}:{self.API_KEY}@api.challonge.com/v1/tournaments/'

        async with aiohttp.ClientSession() as session:
            async with session.get(f'{_URL}{tourId}.json') as response:
                assert response.status == 200
                json_body = await response.json()

        return json_body['tournament']

    @commands.command(name='tour')
    async def _tour(self, ctx):
        """ Extract tournament info from challonge and output it as wikicode. """
        contents = ctx.message.content.split(' ')
        if len(contents) != 2:
            await ctx.send('Message has not the required amount of arguments!')
            return
        else:
            tourUrl = contents[1]
            print(tourUrl)
        if "http://" in tourUrl:
            tourUrl = tourUrl[7:]
        elif "https://" in tourUrl:
            tourUrl = tourUrl[8:]
        urlElements = tourUrl.split('.')
        if len(urlElements) == 2:
            tourId = urlElements[1].split('/')[1]
        elif len(urlElements) == 3:
            tourId = urlElements[0]+'-'+urlElements[2].split('/')[1]
        else:
            return
        tourInfo = await self.fetch_tour(tourId)
        desc = tourInfo['description']
        soup = BeautifulSoup(desc, 'html.parser')
        links = desc.split('href="')
        if "matcherino.com/tournaments/" in desc:
            for i in links:
                if "matcherino.com/tournaments/" in i:
                    print(i.split('" ')[0])
        msg = str(tourInfo['name'])+'\nStarts at: '+str(tourInfo['start_at'])+'\n'+'Sign up: <'+str(tourInfo['full_challonge_url'])+'>'
        if tourInfo['game_id'] != 28273:
            msg += '\n Warning! Game is not set to SC2 LotV.'
        if not tourInfo['open_signup']:
            msg += '\n Warning! Tournament has no open sign ups.'
        await ctx.send(msg)

def setup(bot):
    n = Challonge(bot)
    bot.add_cog(n)
