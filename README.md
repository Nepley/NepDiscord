# NepDiscord

Discord bot using [Nepgeardam](https://github.com/Nepley/Nepgeardam) + some other functionnality

# Requirements

The bot is using [Nextcord](https://github.com/nextcord/nextcord) for the bot part and FastAPI for the Webservices
All library used are in the requirements.txt

A Dockerfile is provided.

The bot need [Nepgeardam](https://github.com/Nepley/Nepgeardam) in order to function properly, the URL is to be put in the config.json

A token for Discord must be provided in the config.json

# Usage

The bot can normally do all the actions that [Nepgeardam](https://github.com/Nepley/Nepgeardam) has.

Moreover, it has two Webservices, one who check for the anniversary when called and one one who check the status of youtube playlist

The 'Playlist-Alarm' part is here to monitor when video are added or deleted (voluntarily or not) from a youtube playlist