from datetime import datetime, timedelta
from discord.ext import commands
import asyncio
import logging
import os
import toml

from .utils.chat_formatting import *
from random import choice as randchoice

log = logging.getLogger(__name__)


class Quotes():
    def __init__(self, bot):
        self.bot = bot
        self.data_path = './data/quotes/'
        self.quote_file = 'quotes.toml'
        if os.path.isdir(self.data_path) is False:
            os.makedirs(self.data_path)
        if os.path.isfile(self.data_path + self.quote_file) is False:
            open(self.data_path+self.quote_file, 'a').close()
        self.quotes = toml.load(self.data_path + self.quote_file)


    def _get_random_quote(self, srv):
        if len(self.quotes['quotes'][srv]) == 0:
            return "There are no saved quotes!"
        return randchoice(self.quotes['quotes'][srv])


    def _get_quote(self, srv, num):
        if num > 0 and num <= len(self.quotes['quotes'][srv]):
            return self.quotes['quotes'][srv][num-1]
        else:
            return "That quote doesn't exist!"


    def _add_quote(self, srv, msg):
        self.quotes['quotes'][srv].append(msg)
        f = open(self.data_path+self.quote_file, 'w')
        toml.dump(self.quotes, f)
        f.close()


    def _edit_quote(self, srv, num, msg):
        if num > 0 and num <= len(self.quotes['quotes'][srv]):
            self.quotes['quotes'][srv][num-1] = msg
            f = open(self.data_path+self.quote_file, 'w')
            toml.dump(self.quotes, f)
            f.close()
        else:
            pass


    @commands.command()
    async def delquote(self, ctx, num: int):
        """ Deletes a quote by its number
            Use !allquotes to find quote numbers
            Example: !delquote 3
        """
        try:
            num = int(num)
        except:
            pass
        if num > 0 and num <= len(self.quotes):
            del self.quotes['quotes'][ctx.guild][num-1]
            f = open(self.data_path+self.quote_file, 'w')
            toml.dump(self.quotes, f)
            f.close()
        else:
            await ctx.channel.send("Quote " + str(num) + " does not exist.")


    @commands.command(name="quote")
    async def quote(self, ctx, *msg: str):
        """ Add/edit quotes or retrieve random/specific one.
            Example: !quote what is magecraft = add quote
                     !quote = get random quote
                     !quote 7 = get quote #7
                     !quote 3 what is magecraft = edit quote #3
        """
        try:
            if len(msg) == 1:
                msg = int(msg[0])
                await ctx.channel.send(self._get_quote(ctx.guild.name, msg))
                return
        except:
            pass
        try:
            num = int(msg[0])
            msg = " ".join(msg[1:])
            self._edit_quote(ctx.guild.name, num, msg)
            await ctx.channel.send("Quote #{} edited to {}".format(num, msg))
            return
        except:
            pass
        msg = " ".join(msg)
        if msg.lstrip() == "":
            await ctx.channel.send(self._get_random_quote(ctx.guild.name))
        else:
            self._add_quote(ctx.guild.name, escape_mass_mentions(msg))
            await ctx.channel.send("Quote added.")


def setup(bot):
    n = Quotes(bot)
    bot.add_cog(n)
