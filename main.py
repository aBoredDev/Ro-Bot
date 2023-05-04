import os
import json
# noinspection PyPackageRequirements
from discord.ext import commands  # 'discord' module comes from 'py-cord' package
# noinspection PyPackageRequirements
import discord  # 'discord' module comes from 'py-cord' package
import logging
from os.path import exists

# epoch must be in the format like "1 January 2020 PST", ie, following the "%d %B %Y %Z" date format.

FORMAT = ('%(asctime)-15s %(threadName)-15s '
          '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

configFile = 'config.json'
if os.path.isfile(configFile):
    with open(configFile) as file:
        conf: dict[str, str | int] = json.load(file)
        discord_token: str = conf['discord_bot_token']
        description: str = conf['description']
        rocode_minute: int = conf['rocode_minute']
        rocode_hour: int = conf['rocode_hour']
        epoch: str = conf['epoch']
        timezone: str = conf['timezone']
        owner: int = conf['owner']
        file.close()
else:
    logger.error('Uh... no config file. Gonna explode now.')

if not exists('./persistent/events.json'):
    with open('./persistent/events.json', 'w') as f:
        json.dump({}, f)
        f.close()

intents = discord.Intents.default() | discord.Intents.message_content

bot = commands.Bot(command_prefix='!', description=description, intents=intents,
                   owner_id=owner)
bot.rocode_minute = rocode_minute
bot.rocode_hour = rocode_hour
bot.epoch_str = epoch
bot.timezone_str = timezone

bot.load_extension('rocode')
bot.load_extension('event_threads')


async def check_owner(ctx: commands.Context) -> bool:
    return await bot.is_owner(ctx.author)


@bot.event
async def on_ready() -> None:
    logger.info(f'Logged in as {bot.user.name} {bot.user.id} \n-----')

if __name__ == '__main__':
    bot.run(discord_token)
