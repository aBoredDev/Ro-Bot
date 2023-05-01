from discord.ext import commands
import discord
import logging
import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz


FORMAT = ('%(asctime)-15s %(threadName)-15s '
          '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('EventThreads')
logger.setLevel(logging.INFO)


class EventThreads(commands.Cog):
    def __init__(self, bot):
        self.forum_channel = 1102381806151536780

        self.bot = bot

        with open('persistent/events.json', 'r') as f:
            self.events = json.load(f)
            f.close()

    @commands.Cog.listener()
    async def on_scheduled_event_create(self, event):
        try:
            ch = self.bot.get_channel(self.forum_channel)
            if ch is None:
                logger.warning('Specifed forum channel does not exist')
            else:
                if event.end_time:
                    when_string = f'**WHEN:** <t:{int(event.start_time.timestamp() // 1)}:F> to <t:{int(event.end_time.timestamp() // 1)}F>\n'
                else:
                    when_string = f'**WHEN:** <t:{int(event.start_time.timestamp() // 1)}:F>\n'

                if event.location:
                    where_string = f'**WHERE:** {event.location}\n'
                else:
                    where_string = f'**WHERE:** Un-specified\n'

                if event.description:
                    description = f'{event.description}\n'
                else:
                    description = 'No description given.\n'

                starter_message = (
                    f'{when_string}'
                    f'{where_string}'
                    f'*Event created by: <@{event.creator_id}>*\n\n'
                    f'{event.description}'
                )

                thread, _ = await ch.create_thread(
                    name=event.name,
                    content=starter_message,
                    reason='Automatically created when a scheduled event was created'
                )

                self.events[str(event.id)] = thread.id
                with open('persistent/events.json', 'w') as f:
                    json.dump(self.events, f)
                    f.close()
                logger.info(f'Created forum channel post {thread.id} for scheduled event {event.id} [{event.name}]')
        except discord.Forbidden:
            logger.warning("Could not create post, Forbidden error")
        except discord.HTTPException:
            logger.warning("Could not create post, HTTP error")

    @commands.Cog.listener()
    async def on_scheduled_event_update(self, before, after):
        if str(before.id) not in self.events.keys():
            return 0
        try:
            ch = self.bot.get_channel(self.forum_channel)
            if ch is None:
                logger.warning('Specifed forum channel does not exist')
            else:
                thread = await self.bot.fetch_channel(self.events[str(before.id)])
                if before.start_time != after.start_time \
                        or before.end_time != after.end_time \
                        or before.location != after.location \
                        or before.description != after.description:
                    if after.end_time:
                        when_string = f'**WHEN:** <t:{int(after.start_time.timestamp() // 1)}:F> to <t:{int(after.end_time.timestamp() // 1)}:F>\n'
                    else:
                        when_string = f'**WHEN:** <t:{int(after.start_time.timestamp() // 1)}:F>\n'

                    if after.location:
                        where_string = f'**WHERE:** {after.location}\n'
                    else:
                        where_string = f'**WHERE:** Un-specified\n'

                    if after.description:
                        description = f'{after.description}\n'
                    else:
                        description = 'No description given.\n'

                    new_message = (
                        f'{when_string}'
                        f'{where_string}'
                        f'*Event created by: <@{after.creator_id}>*\n\n'
                        f'{after.description}'
                    )

                    starter_message = await thread.fetch_message(thread.id)
                    await starter_message.edit(content=new_message)

                if before.name != after.name:
                    await thread.edit(
                        name=after.name,
                        reason='Associated event updated'
                    )

                logger.info(f'Updated forum channel post {thread.id} for scheduled event {after.id} [{after.name}]')
        except discord.Forbidden:
            logger.warning("Could not create post, Forbidden error")
        except discord.HTTPException:
            logger.warning("Could not create post, HTTP error")


async def setup(bot):
    await bot.add_cog(EventThreads(bot))


async def teardown(bot):
    await bot.remove_cog('Rocode')

