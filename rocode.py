import datetime
import pytz
import random
import discord
import logging

from random import shuffle
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands

FORMAT = ('%(asctime)-15s %(threadName)-15s '
          '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('RoCode')
logger.setLevel(logging.INFO)


class Rocode(commands.Cog):

    def __init__(self, bot):
        self.tz = pytz.timezone(bot.timezone_str)  # https://www.youtube.com/watch?v=-5wpm-gesOY
        self.epoch = datetime.datetime.strptime(bot.epoch_str, "%M %H %d %B %Y")
        self.epoch = self.tz.localize(self.epoch)
        logger.info(f"Rocode set to send messages at every {bot.rocode_hour}:{bot.rocode_minute}{self.tz}")

        codefile = open("codes.txt")
        self.codes = codefile.readlines()
        random.seed(1)  # seed random so we shuffle to the same state on each startup
        shuffle(self.codes)

        self.rocodeChannel = {
            "test": 752618760975941643,  # testing server / channel
            "prod": 837825838359511060  # production server / channel
        }

        self.bot = bot

        self.scheduler = AsyncIOScheduler()
        self.rocode_job = self.scheduler.add_job(self.perform_job, trigger='cron', minute=bot.rocode_minute,
                                                 hour=bot.rocode_hour, day='*', week='*', month='*', year='*',
                                                 misfire_grace_time=100, coalesce=False, timezone=self.tz)
        self.scheduler.start()

    def cog_unload(self):
        """
        Remove the rocode jobs and safely shutdown the scheduler
        :return: Nothing
        """
        self.rocode_job.remove()
        self.scheduler.shutdown()

    async def perform_job(self):
        logger.info("Performing Rocode Job at " + datetime.datetime.now(tz=self.tz).strftime("%d-%m-%Y--%H-%M"))
        curr_code = self.codes[(datetime.datetime.now(tz=self.tz) - self.epoch).days % len(self.codes)]
        for server, channel in self.rocodeChannel.items():
            try:
                ch = self.bot.get_channel(channel)
                if ch is None:
                    logger.info("Skipping server with no perms or non-existent channel ID")
                else:
                    await self.bot.get_channel(channel).send(curr_code)
            except discord.Forbidden:
                logger.warning("Could not send ro'code, Forbidden error")
            except discord.HTTPException:
                logger.warning("Could not send ro'code, HTTP error")

    # Users can manually retrieve the current rocode using this command in discord
    @commands.command(pass_context=True)
    async def rocode(self, ctx):
        curr_code = self.codes[(datetime.datetime.now(tz=self.tz) - self.epoch).days % len(self.codes)]
        await ctx.channel.send("Today's Rover Code is:\n\n" + curr_code)


def setup(bot):
    bot.add_cog(Rocode(bot))


def teardown(bot):
    bot.remove_cog('Rocode')
