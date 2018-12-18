import toml


def get(ctx):
    data_path = './data/bot/'
    perm_file = 'perms.toml'
    perms = toml.load(data_path + perm_file)
    conf_file = 'conf.toml'
    conf = toml.load(data_path + conf_file)

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


def check(ctx, lvl):
    return get(ctx) >= lvl
