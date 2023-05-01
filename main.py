import os
import json
from discord.ext import commands
import discord
import logging
from os.path import exists

# epoch must be in the format like "1 January 2020 PST", ie, following the "%d %B %Y %Z" date format.

FORMAT = ('%(asctime)-15s %(threadName)-15s '
          '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('Main')
logger.setLevel(logging.INFO)

configFile = "config.json"
if os.path.isfile(configFile):
    with open(configFile) as file:
        conf = json.load(file)
        discord_token = conf['discord_bot_token']
        description = conf['description']
        rocode_minute = conf['rocode_minute']
        rocode_hour = conf['rocode_hour']
        epoch = conf['epoch']
        timezone = conf['timezone']
        owner = conf['owner']
        file.close()
else:
    logger.error("Uh... no config file. Gonna explode now.")

if not exists('./persistent/events.json'):
    with open('./persistent/events.json', 'w') as f:
        json.dump({}, f)
        f.close()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', description=description, intents=intents)
bot.rocode_minute = rocode_minute
bot.rocode_hour = rocode_hour
bot.epoch_str = epoch
bot.timezone_str = timezone


def check_owner(ctx):
    return bot.is_owner(ctx.author)


@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name} {bot.user.id} \n-----')
    await bot.load_extension("rocode")
    await bot.load_extension('event_threads')

if __name__ == '__main__':
    bot.run(discord_token)
