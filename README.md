# Adjutant Discord Bot

[![Adjutant Support Server](https://discordapp.com/api/guilds/391304338099929092/widget.png?style=shield)](https://discord.gg/nfa9jnu)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/44aba3b6bffa481c83432b835d8bd4f9)](https://app.codacy.com/app/K4cePhoenix/Adjutant-DiscordBot?utm_source=github.com&utm_medium=referral&utm_content=K4cePhoenix/Adjutant-DiscordBot&utm_campaign=badger)
[![GPLv3 License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://github.com/K4cePhoenix/Adjutant-DiscordBot/blob/master/LICENSE)

**Adjutant** is a personal Discord bot written in [Python](https://www.python.org "Python homepage") 3.6+ using [discord.py](https://github.com/Rapptz/discord.py).

She handles [StarCraft II](https://starcraft2.com/) related tasks and commands utilising information from [Liquipedia](http://liquipedia.net/).

## Commands

- set channel [event_type] [new-channel-name]

Change the target channel for a specific event type (general, amateur, team).
*Requires permission level 3.*

## Permissions system

**Adjutant** uses a 5-level permissions system to allow usage of her commands (not yet fully implemented).

Level 4: Server Owner

Level 3: Administrators

Level 2: Moderators

Level 1: Members

Level 0: Bots

## Requirements

- [Python](https://www.python.org "Python homepage") 3.6+
- [discord.py](https://github.com/Rapptz/discord.py) v1.0.0a
- [beautifulsoup4](https://pypi.python.org/pypi/beautifulsoup4) 4.6.0
- [toml](https://pypi.python.org/pypi/toml) 0.9.4
- [pytz](https://pypi.python.org/pypi/pytz/2017.3) 2017.3
