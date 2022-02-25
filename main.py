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
    with open(configFile) as file:
        conf = json.load(file)
        discord_token = conf["discord_bot_token"]
        description = conf['description']
        rocode_minute = conf['rocode_minute']
        rocode_hour = conf['rocode_hour']
        epoch = conf['epoch']
        timezone = conf['timezone']
        owner = conf['owner']
        file.close()
else:
    logger.error("Uh... no config file. Gonna explode now.")

bot = commands.Bot(command_prefix='!', description=description)
bot.rocode_minute = rocode_minute
bot.rocode_hour = rocode_hour
bot.epoch_str = epoch
bot.timezone_str = timezone
bot.load_extension("rocode")


def check_owner(ctx):
    return bot.is_owner(ctx.author)


@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name} {bot.user.id} \n-----')


@bot.command(hidden=True)
@commands.check(check_owner)
async def reload(ctx):
    """Reloads the specified extension.
    """
    try:
        bot.reload_extension('rocode')
    except commands.ExtensionNotFound:
        await ctx.send(':x: Ro-Code extension could not be found!', delete_after=10.0)
        logger.warning('Ro-Code extension could not be found!')
    except commands.ExtensionNotLoaded:
        await ctx.send(':x: Ro-Code extension was not loaded!', delete_after=10.0)
        logger.warning('Ro-Code extension was not loaded!')
    except commands.ExtensionFailed:
        await ctx.send(':x: Ro-Code extension failed during setup!', delete_after=10.0)
        logger.warning('Ro-Code extension failed during setup')
    else:
        await ctx.send(':white_check_mark: Ro-Code extension reloaded successfully!', delete_after=10.0)
        logger.info('Ro-Code extension reloaded')

if __name__ == '__main__':
    bot.run(discord_token)
