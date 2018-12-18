from discord.ext import commands
import aiohttp


class Challonge:
    def __init__(self, bot):
        self.bot = bot
        self.API_KEY = self.bot.CONFIG['api']['challonge_token']
        self.USERNAME = self.bot.CONFIG['api']['challonge_uname']

    async def fetch_tour(self, tournament_id):
        _URL = f'https://{self.USERNAME}:{self.API_KEY}@api.challonge.com/v1/tournaments/'

        async with aiohttp.ClientSession() as session:
            async with session.get(f'{_URL}{tournament_id}.json') as response:
                if not response.status == 200:
                    raise AssertionError()
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
            tournament_url = contents[1]
            print(tournament_url)
        if "http://" in tournament_url:
            tournament_url = tournament_url[7:]
        elif "https://" in tournament_url:
            tournament_url = tournament_url[8:]
        url_elements = tournament_url.split('.')
        if len(url_elements) == 2:
            tournament_id = url_elements[1].split('/')[1]
        elif len(url_elements) == 3:
            tournament_id = url_elements[0]+'-'+url_elements[2].split('/')[1]
        else:
            return
        tournament_info = await self.fetch_tour(tournament_id)
        desc = tournament_info['description']
        links = desc.split('href="')
        if "matcherino.com/tournaments/" in desc:
            for i in links:
                if "matcherino.com/tournaments/" in i:
                    print(i.split('" ')[0])
        msg = str(tournament_info['name'])+'\nStarts at: '+str(tournament_info['start_at'])+'\n'+'Sign up: <'+str(tournament_info['full_challonge_url'])+'>'
        if tournament_info['game_id'] != 28273:
            msg += '\n Warning! Game is not set to SC2 LotV.'
        if not tournament_info['open_signup']:
            msg += '\n Warning! Tournament has no open sign ups.'
        await ctx.send(msg)


def setup(bot):
    n = Challonge(bot)
    bot.add_cog(n)
