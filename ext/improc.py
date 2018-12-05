from discord.ext import commands
from PIL import Image, ImageChops, ImageOps
from io import BytesIO
# from tempfile import TemporaryFile
from time import time
import numpy as np
import aiohttp
import discord
import logging
import requests

from .utils import permissions as perms
from .utils import image_processing as improc


log = logging.getLogger('adjutant.improc')


class ImageProcessing:
    def __init__(self, bot):
        self.bot = bot

    async def send_image(self, ctx, i, t, u):
        f = BytesIO()
        i.save(f, format='PNG')
        await ctx.send(f"It took {t:.3f}s to perform this task.", 
                        file=discord.File(f.getvalue(), 
                        filename=f"{ctx.message.content.split('ava ')[1].split(' ')[0]}_avatar_{u.name}-{u.discriminator}.png")
        )

    async def url_to_image(self, url):
        # async with aiohttp.ClientSession() as session:
        #     async with session.get(url) as resp:
        #         cont = await resp.content.read()
        #         image_file = io.BytesIO(cont)
        #         image = Image.open(image_file)
        r = requests.get(url)
        img = Image.open(BytesIO(r.content))
        img = img.resize((512, 512,), resample=Image.LANCZOS)
        return img

    @commands.group(name='ava')
    async def _avatar(self, ctx):
        if perms._check(ctx, 5):
            pass
        else:
            await ctx.send('You have no permissions to execute this command.')
            raise PermissionError()


    @_avatar.command(name='invert', aliases=['inv'])
    async def _avatar_invert(self, ctx):
        try:
            user = ctx.message.mentions[0]
        except Exception:
            user = ctx.message.author
        start_time = time()
        img = await self.url_to_image(user.avatar_url_as(format='png', size=1024))
        img = improc.invert_image(img)
        total_time = time()-start_time
        await self.send_image(ctx, img, total_time, user)

    @_avatar.command(name='equalise', aliases=['equalize', 'eq'])
    async def _avatar_equalise(self, ctx):
        try:
            user = ctx.message.mentions[0]
        except Exception:
            user = ctx.message.author
        start_time = time()
        img = await self.url_to_image(user.avatar_url_as(format='png', size=1024))
        img = improc.hist_equalise(img)
        total_time = time()-start_time
        await self.send_image(ctx, img, total_time, user)

    @_avatar.command(name='histogram', aliases=['histo', 'hist'])
    async def _avatar_equalise(self, ctx):
        try:
            user = ctx.message.mentions[0]
        except Exception:
            user = ctx.message.author
        start_time = time()
        img = await self.url_to_image(user.avatar_url_as(format='png', size=1024))
        img2 = improc.histogram(img, user)
        total_time = time()-start_time
        # await ctx.send(f"time: {total_time}",file=discord.File(f.getvalue(), filename=f'inv_ava_{user.name}-{user.discriminator}.png'))
        await self.send_image(ctx, img2, total_time, user)

    @_avatar.command(name='grey', aliases=['gray'])
    async def _avatar_grey(self, ctx):
        try:
            user = ctx.message.mentions[0]
        except Exception:
            user = ctx.message.author
        start_time = time()
        img = await self.url_to_image(user.avatar_url_as(format='png', size=1024))
        img = improc.greyscale_image(img)
        total_time = time()-start_time
        await self.send_image(ctx, img, total_time, user)

    @_avatar.command(name='websafe', aliases=['ws'])
    async def _avatar_websafe(self, ctx):
        try:
            user = ctx.message.mentions[0]
        except Exception:
            user = ctx.message.author
        start_time = time()
        img = await self.url_to_image(user.avatar_url_as(format='png', size=1024))
        img = improc.websafe(img)
        total_time = time()-start_time
        await self.send_image(ctx, img, total_time, user)

    @_avatar.command(name='smooth', aliases=['blur'])
    async def _avatar_smooth(self, ctx, _type=None):
        try:
            user = ctx.message.mentions[0]
        except Exception:
            user = ctx.message.author
        start_time = time()
        img = await self.url_to_image(user.avatar_url_as(format='png', size=1024))
        img = improc.smooth(img, _type)
        total_time = time()-start_time
        await self.send_image(ctx, img, total_time, user)

def setup(bot):
    n = ImageProcessing(bot)
    bot.add_cog(n)
    