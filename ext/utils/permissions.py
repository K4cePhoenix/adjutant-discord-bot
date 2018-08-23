import toml


def _get(ctx):
    data_path = './data/bot/'
    perm_file = 'perms.toml'
    perms = toml.load(data_path + perm_file)
    conf_file = 'conf.toml'
    conf = toml.load(data_path + conf_file)

    if ctx.message.author.bot:
        return 0
    lvl = [0]
    # for r in ctx.message.author.roles:
    #     if r.name in perms[ctx.guild.name]['lvl3']:
    #         lvl.append(3)
    #     elif r.name in perms[ctx.guild.name]['lvl2']:
    #         lvl.append(2)
    #     elif r.name in perms[ctx.guild.name]['lvl1']:
    #         lvl.append(1)
    if ctx.message.author.id == conf['owner']['id'] and ctx.guild.id == 391304338099929092:
        lvl.append(5)
    for i in perms["moderators"]:
        if ctx.message.author.id == perms["moderators"][i] and ctx.guild.id == 391304338099929092:
            lvl.append(4)
    if ctx.message.author.guild_permissions.administrator:
        lvl.append(3)
    if ctx.message.author.guild_permissions.manage_guild:
        lvl.append(2)
    else:
        lvl.append(1)

    return max(lvl)


def _check(ctx, lvl):
    return _get(ctx) >= lvl
