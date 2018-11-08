from discord.ext import commands
import aiosqlite
import logging

from .utils import permissions as perms


log = logging.getLogger(__name__)


class Settings():
    def __init__(self, bot):
        self.bot = bot


    async def _get_db_entry(self, sql, val):
        async with aiosqlite.connect('./data/db/adjutant.sqlite3') as db:
            try:
                cursor = await db.execute(sql, val)
                data = await cursor.fetchone()
                await cursor.close()
                return data[0]
            except Exception as e:
                log.debug(f'rss module _get_db_entry - {e}')
                return None


    async def _set_db_entry(self, sql, val):
        async with aiosqlite.connect('./data/db/adjutant.sqlite3') as db:
            try:
                await db.execute(sql, val)
                ret = True
            except:
                await db.rollback()
                ret = False
            finally:
                await db.commit()
                return ret


    @commands.group(name='set')
    async def _settings(self, ctx):
        """ Change a setting """
        if perms._check(ctx, 3):
            pass
        else:
            await ctx.send('You have no permissions to execute this command.')
            raise PermissionError()


    @_settings.command(name='general')
    async def _settings_general(self, ctx, *, t: str):
        """ Set the channel name for general events """
        if t in ["delete", "reset"]:
            temp_name = '-'
            temp_id = -1
            sql = "UPDATE guilds SET gcid = ?, gcname = ? WHERE id = ?;"
            ret = await self._set_db_entry(sql, (temp_id, temp_name, ctx.guild.id,))
        elif t[:2] == "<#":
            temp_name = self.bot.get_channel(int(t[2:-1]))
            sql = "UPDATE guilds SET gcid = ?, gcname = ? WHERE id = ?;"
            ret = await self._set_db_entry(sql, (t[2:-1], temp_name.name, ctx.guild.id,))
        else:
            for channel in ctx.guild.channels:
                if channel.name == t:
                    temp_name = self.bot.get_channel(channel.id)
                    break
            if temp_name:
                sql = "UPDATE guilds SET gcid = ?, gcname = ? WHERE id = ?;"
                ret = await self._set_db_entry(sql, (temp_name.id, temp_name.name, ctx.guild.id,))
        if ret:
            await ctx.message.add_reaction('☑')
        else:
            await ctx.message.add_reaction('❌')


    @_settings.command(name='amateur')
    async def _settings_amateur(self, ctx, *, t: str):
        """ Set the channel name for amateur events """
        if t in ["delete", "reset"]:
            temp_name = '-'
            temp_id = -1
            sql = "UPDATE guilds SET acid = ?, acname = ? WHERE id = ?;"
            ret = await self._set_db_entry(sql, (temp_id, temp_name, ctx.guild.id,))
        elif t[:2] == "<#":
            temp_name = self.bot.get_channel(int(t[2:-1]))
            sql = "UPDATE guilds SET acid = ?, acname = ? WHERE id = ?;"
            ret = await self._set_db_entry(sql, (t[2:-1], temp_name.name, ctx.guild.id,))
        else:
            for channel in ctx.guild.channels:
                if channel.name == t:
                    temp_name = self.bot.get_channel(channel.id)
                    break
            if temp_name:
                sql = "UPDATE guilds SET acid = ?, acname = ? WHERE id = ?;"
                ret = await self._set_db_entry(sql, (temp_name.id, temp_name.name, ctx.guild.id,))
            else:
                await ctx.send(f"Can't find a channel named `{t}`")
        if ret:
            await ctx.message.add_reaction('☑')
        else:
            await ctx.message.add_reaction('❌')

    @_settings.command(name='team')
    async def _settings_team(self, ctx, *, t: str):
        """ Set the channel name for team events """
        pass


    @_settings.command(name='timeformat', aliases=['time', 'tf'])
    async def _settings_timeformat(self, ctx, *, t: int):
        """ Set the timeformat (24h- or 12ham/pm-format) """
        async with aiosqlite.connect('./data/db/adjutant.sqlite3') as db:
            try:
                if 12 == t:
                    tmp = 0
                elif 24 == t:
                    tmp = 1
                sql = "UPDATE guilds SET tf = ? WHERE id = ?;"
                await db.execute(sql, (tmp, ctx.guild.id,))
                if tmp:
                    await ctx.channel.send('Changed the time format to 24h')
                else:
                    await ctx.channel.send('Changed the time format to 12h am/pm')
            except:
                await db.rollback()
                await ctx.channel.send('**ERROR**: Could not change time format. Can only set time format to `12` or `24`')
            finally:
                await db.commit()


    @_settings.command(name='message', aliases=['msg',])
    async def _settings_message(self, ctx, *, t: str):
        """ Customise the message printed along tournament information """
        if len(t.split('"')) == 3:
            tmp = t.split('"')[1]
            sql = "UPDATE guilds SET evmessage = ? WHERE id = ?;"
            ret = await self._set_db_entry(sql, (tmp, ctx.guild.id,))
        if ret:
            await ctx.message.add_reaction('☑')
        else:
            await ctx.message.add_reaction('❌')

    @commands.command(name='events')
    async def _settings_events(self, ctx, _type=None, *, t: str = None):
        if perms._check(ctx, 3):
            if _type == "all":
                sql = "UPDATE guilds SET events = ? WHERE id = ?"
                ret = await self._set_db_entry(sql, ("*", ctx.guild.id,))
            elif _type == "add":
                sql = "SELECT events FROM guilds WHERE id = ?"
                data = await self._get_db_entry(sql, (ctx.guild.id,))
                if data and t:
                    if not "$" in t:
                        data_list = data.split('$')
                        data_list.append(t)
                        sql = "UPDATE guilds SET events = ? WHERE id = ?"
                        ret = await self._set_db_entry(sql, ('$'.join(data_list), ctx.guild.id,))
            elif _type == "del":
                sql = "SELECT events FROM guilds WHERE id = ?"
                data = await self._get_db_entry(sql, (ctx.guild.id,))
                if data and t:
                    if not "$" in t:
                        data_list = data.split('$')
                        for ind, item in enumerate(data_list):
                            if item == t:
                                data_list = data_list[:ind] + data_list[ind+1:]
                                break
                        sql = "UPDATE guilds SET events = ? WHERE id = ?"
                        ret = await self._set_db_entry(sql, ('$'.join(data_list), ctx.guild.id,))
            elif _type == "show":
                sql = "SELECT events FROM guilds WHERE id = ?"
                data = await self._get_db_entry(sql, (ctx.guild.id,))
                if data:
                    data_list = data.split('$')
                    data_send = ', '.join(data_list)
                    if data_send == '*':
                        await ctx.send("All events will be posted!")
                    else:
                        await ctx.send(f"Currently events including `{data_send}` will be posted.")
            else:
                ctx.send("**ERROR**: Couldn't execute your request ")
            if ret:
                await ctx.message.add_reaction('☑')
            else:
                await ctx.message.add_reaction('❌')

    @commands.command(name='listchannels', aliases=['list', 'lc'])
    async def _list_channels(self, ctx):
        if perms._check(ctx, 2):
            async with aiosqlite.connect('./data/db/adjutant.sqlite3') as db:
                sql = f"SELECT * FROM guilds WHERE id = ?;"
                cursor = await db.execute(sql, (ctx.guild.id,))
                tmp_guild = await cursor.fetchone()
                await cursor.close()
            await ctx.channel.send(f'The currently set SC2 event channels are\nGeneral Events Channel: <#{tmp_guild[2]}>\nAmateur Events Channel: <#{tmp_guild[4]}>')


def setup(bot):
    n = Settings(bot)
    bot.add_cog(n)
