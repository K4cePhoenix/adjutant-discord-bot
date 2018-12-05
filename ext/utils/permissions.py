import toml


def _get(ctx):
    DATA_PATH = './data/bot/'
    PERM_FILE = 'perms.toml'
    perms = toml.load(DATA_PATH + PERM_FILE)
    CONF_FILE = 'conf.toml'
    conf = toml.load(DATA_PATH + CONF_FILE)

    if ctx.message.author.bot:
        return 0
    elif ctx.message.author.id == conf['owner']['id'] and ctx.guild.id == 391304338099929092:
        return 5
    elif ctx.message.author.id in perms["moderators"] and ctx.guild.id == 391304338099929092:
        return 4
    elif ctx.message.author.guild_permissions.administrator:
        return 3
    elif ctx.message.author.guild_permissions.manage_guild:
        return 2
    else:
        return 1


def _check(ctx, lvl):
    return _get(ctx) >= lvl
