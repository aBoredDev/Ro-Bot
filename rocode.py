import datetime
import pytz
import random
# noinspection PyPackageRequirements
import discord  # 'discord' module comes from 'py-cord' package
# noinspection PyPackageRequirements
from discord.ext import commands  # 'discord' module comes from 'py-cord' package
import logging
from random import shuffle
from apscheduler.schedulers.asyncio import AsyncIOScheduler

FORMAT = ('%(asctime)-15s %(threadName)-15s '
          '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)


class Rocode(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.tz = pytz.timezone(bot.timezone_str)  # https://www.youtube.com/watch?v=-5wpm-gesOY
        self.epoch = datetime.datetime.strptime(bot.epoch_str, '%M %H %d %B %Y')
        self.epoch = self.tz.localize(self.epoch)
        logger.info(f'Rocode set to send messages at {bot.rocode_hour}:{bot.rocode_minute} in {self.tz}')

        codefile = open('codes.txt')
        self.codes = codefile.readlines()
        random.seed(1)  # seed random so we shuffle to the same state on each startup
        shuffle(self.codes)

        self.rocodeChannel = {
            'test': 752618760975941643,  # testing server / channel
            'prod': 837825838359511060  # production server / channel
        }

        self.bot = bot

        self.scheduler = AsyncIOScheduler()
        self.rocode_job = self.scheduler.add_job(
            self.perform_job, trigger='cron', minute=bot.rocode_minute,
            hour=bot.rocode_hour, day='*', week='*', month='*', year='*',
            misfire_grace_time=100, coalesce=False, timezone=self.tz)
        self.scheduler.start()

    def cog_unload(self) -> None:
        """
        Remove the rocode jobs and safely shutdown the scheduler
        :return: Nothing
        """
        self.rocode_job.remove()
        self.scheduler.shutdown()

    async def perform_job(self) -> None:
        logger.info('Performing Rocode Job at ' + datetime.datetime.now(tz=self.tz).strftime('%d-%m-%Y--%H-%M'))
        curr_code = self.codes[(datetime.datetime.now(tz=self.tz) - self.epoch).days % len(self.codes)]
        for server, channel in self.rocodeChannel.items():
            try:
                ch = self.bot.get_channel(channel)
                if ch is None:
                    logger.info('Skipping server with no perms or non-existent channel ID')
                    continue
                await self.bot.get_channel(channel).send(curr_code)
            except discord.Forbidden as err:
                logger.warning("Could not send ro'code, Forbidden error", exc_info=err)
            except discord.HTTPException as err:
                logger.warning("Could not send ro'code, HTTP error", exc_info=err)

    # Users can manually retrieve the current rocode using this command in discord
    @commands.slash_command(name='rocode', description='Get today\'s rocode')
    async def rocode(self, ctx: commands.Context) -> None:
        curr_code = self.codes[(datetime.datetime.now(tz=self.tz) - self.epoch).days % len(self.codes)]
        await ctx.response.send_message("Today's Rover Code is:\n\n" + curr_code)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Rocode(bot))


def teardown(bot: commands.Bot) -> None:
    bot.remove_cog('Rocode')
