# Adjutant Discord Bot

**Adjutant** is a personal Discord bot written in [Python](https://www.python.org "Python homepage") 3.6+ using [discord.py](https://github.com/Rapptz/discord.py).

She handles [StarCraft II](https://starcraft2.com/) related tasks and commands utilising information from [Liquipedia](http://liquipedia.net/).

## Commands

- set channel [event_type] [new-channel-name]

Change the target channel for a specific event type (general, amateur, team).
*Requires permission level 3.*

## Permissions system

**Adjutant** uses a 5-level permissions system to allow usage of her commands (not yet fully implemented).

Level 4: Bot Owner

Level 3: Server Owner

Level 2: Administrators

Level 1: Moderators

Level 0: Members and Bots

## Requirements

- [Python](https://www.python.org "Python homepage") 3.6+
- [discord.py](https://github.com/Rapptz/discord.py) v1.0.0a
- [beautifulsoup4](https://pypi.python.org/pypi/beautifulsoup4) 4.6.0
- [toml](https://pypi.python.org/pypi/toml) 0.9.4
- [pytz](https://pypi.python.org/pypi/pytz/2017.3) 2017.3
