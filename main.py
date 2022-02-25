import os
import json
from discord.ext import commands
import logging

# epoch must be in the format like "1 January 2020 PST", ie, following the "%d %B %Y %Z" date format.

FORMAT = ('%(asctime)-15s %(threadName)-15s '
          '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('Main')
logger.setLevel(logging.INFO)

configFile = "config.json"
if os.path.isfile(configFile):
    file = open(configFile)
    conf = json.load(file)
    discord_token = conf["discord_bot_token"]
    description = conf['description']
    rocode_minute = conf['rocode_minute']
    rocode_hour = conf['rocode_hour']
    epoch = conf['epoch']
    timezone = conf['timezone']
else:
    logger.error("Uh... no config file. Gonna explode now.")

bot = commands.Bot(command_prefix='!', description=description)
bot.rocode_minute = rocode_minute
bot.rocode_hour = rocode_hour
bot.epoch_str = epoch
bot.timezone_str = timezone
bot.load_extension("rocode")


@bot.event
async def on_ready():
    logger.info('Logged in as', bot.user.name, bot.user.id, '\n-----')


if __name__ == '__main__':
    bot.run(discord_token)
