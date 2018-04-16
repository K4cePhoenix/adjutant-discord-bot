import toml

data_path = './data/bot/'
perm_file = 'perms.toml'
perms = toml.load(data_path + perm_file)

def _get(ctx):
    lvl = [0]
    for r in ctx.message.author.roles:
        if r.name in perms[ctx.guild.name]['lvl3']:
            lvl.append(3)
        elif r.name in perms[ctx.guild.name]['lvl2']:
            lvl.append(2)
        elif r.name in perms[ctx.guild.name]['lvl1']:
            lvl.append(1)
        elif ctx.message.author.guild_permissions.administrator:
            lvl.append(3)
        elif ctx.message.author.guild_permissions.manage_guild:
            lvl.append(2)
    print(lvl, max(lvl))

    return max(lvl)


def _check(ctx, lvl):
    return _get(ctx) >= lvl
