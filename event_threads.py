# noinspection PyPackageRequirements
from discord.ext import commands  # 'discord' module comes from 'py-cord' package
# noinspection PyPackageRequirements
import discord  # 'discord' module comes from 'py-cord' package
import logging
import json
import datetime
import pytz


FORMAT = ('%(asctime)-15s %(threadName)-15s '
          '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)


class EventThreads(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.forum_channels = {
            '719753220670619660': 1102381806151536780  # testing server
        }

        self.bot = bot

        with open('persistent/events.json', 'r') as f:
            self.events = json.load(f)
            f.close()

        for guild in self.forum_channels.keys():
            if guild not in self.events.keys():
                self.events[guild] = {}

        with open('persistent/events.json', 'w') as f:
            json.dump(self.events, f)
            f.close()

    @commands.Cog.listener()
    async def on_scheduled_event_create(self,
                                        event: discord.ScheduledEvent) -> None:
        if str(event.guild.id) not in self.forum_channels.keys():
            return

        try:
            ch = self.bot.get_channel(self.forum_channels[str(event.guild.id)])
            if ch is None:
                logger.warning('Specifed forum channel does not exist')
            else:
                if event.end_time:
                    when_string = f'**WHEN:** <t:{int(event.start_time.timestamp() // 1)}:F> to ' \
                                  f'<t:{int(event.end_time.timestamp() // 1)}F>\n'
                else:
                    when_string = f'**WHEN:** <t:{int(event.start_time.timestamp() // 1)}:F>\n'

                if event.location.type == discord.ScheduledEventLocationType.external:
                    where_string = f'**WHERE:** {event.location.value}\n'
                else:
                    where_string = f'**WHERE:** {event.location.value.mention}\n'

                if event.description:
                    description = f'{event.description}\n'
                else:
                    description = 'No description given.\n'

                starter_message = (
                    f'{when_string}'
                    f'{where_string}'
                    f'*Event created by: <@{event.creator_id}>*\n\n'
                    f'{description}\n'
                    f'{event.url}'
                )

                thread = await ch.create_thread(
                    name=event.name,
                    content=starter_message,
                    reason='Automatically created when a scheduled event was created'
                )

                self.events[str(event.guild.id)][str(event.id)] = thread.id
                with open('persistent/events.json', 'w') as f:
                    json.dump(self.events, f)
                    f.close()
                logger.info(f'Created forum channel post {thread.id} for '
                            f'scheduled event {event.id} [{event.name}]')
        except discord.Forbidden as err:
            logger.warning('Could not create post, Forbidden error', exc_info=err)
        except discord.HTTPException as err:
            logger.warning('Could not create post, HTTP error', exc_info=err)

    @commands.Cog.listener()
    async def on_scheduled_event_delete(self, event: discord.ScheduledEvent) -> None:
        if str(event.guild.id) not in self.forum_channels.keys():
            return
        if str(event.id) not in self.events[str(event.guild.id)].keys():
            return

        try:
            ch = self.bot.get_channel(self.forum_channels[str(event.guild.id)])
            if ch is None:
                logger.warning(f'Specifed forum channel {self.forum_channels[str(event.guild.id)]} for guild '
                               f'{event.guild.id} does not exist')
                return

            thread = await self.bot.fetch_channel(self.events[str(event.guild.id)][str(event.id)])
            if thread is None:
                logger.warning(f'Specified thread "{self.events[str(event.guild.id)][str(event.id)]}" for event'
                               f'"{event.id}" does not exist')
                return
            
            time = int(datetime.datetime.now(tz=pytz.timezone('UTC')).timestamp() // 1)
            if event.status == discord.ScheduledEventStatus.canceled:
                # Because of discord's backend implementation of event cancellation, the status doesn't actually change
                # to cancelled when the event is cancelled, it remains as scheduled
                # See https://github.com/discord/discord-api-docs/issues/4105
                await thread.send(f'**===== EVENT CANCELLED <t:{time}:F> =====**')
                self.events[str(event.guild.id)].pop(str(event.id))
                with open('persistent/events.json', 'w') as f:
                    json.dump(self.events, f)
                    f.close()
            logger.info(f'Updated forum channel post {thread.id} for deleted event {event.id} [{event.name}]')
        except discord.Forbidden as err:
            logger.warning('Could not create post, Forbidden error', exc_info=err)
        except discord.HTTPException as err:
            logger.warning('Could not create post, HTTP error', exc_info=err)

    @commands.Cog.listener()
    async def on_scheduled_event_update(self, before: discord.ScheduledEvent,
                                        after: discord.ScheduledEvent) -> None:
        if str(before.guild.id) not in self.forum_channels.keys():
            return
        if str(before.id) not in self.events[str(before.guild.id)].keys():
            return

        try:
            ch = self.bot.get_channel(self.forum_channels[str(before.guild.id)])
            if ch is None:
                logger.warning(f'Specifed forum channel {self.forum_channels[str(before.guild.id)]} for guild '
                               f'{before.guild.id} does not exist')
                return
            
            thread = await self.bot.fetch_channel(
                self.events[str(before.guild.id)][str(before.id)])
            if thread is None:
                logger.warning(f'Specified thread "{self.events[str(before.guild.id)][str(before.id)]}" for event'
                               f'"{before.id}" does not exist')
                return

            if before.start_time != after.start_time \
                    or before.end_time != after.end_time \
                    or before.location != after.location \
                    or before.description != after.description:
                if after.end_time:
                    when_string = f'**WHEN:** <t:{int(after.start_time.timestamp() // 1)}:F> to ' \
                                  f'<t:{int(after.end_time.timestamp() // 1)}:F>\n'
                else:
                    when_string = f'**WHEN:** <t:{int(after.start_time.timestamp() // 1)}:F>\n'

                if after.location.type == discord.ScheduledEventLocationType.external:
                    where_string = f'**WHERE:** {after.location.value}\n'
                else:
                    where_string = f'**WHERE:** {after.location.value.mention}\n'

                if after.description:
                    description = f'{after.description}\n'
                else:
                    description = 'No description given.\n'

                new_message = (
                    f'{when_string}'
                    f'{where_string}'
                    f'*Event created by: <@{after.creator_id}>*\n\n'
                    f'{description}\n'
                    f'{after.url}'
                )

                starter_message = thread.get_partial_message(thread.id)
                await starter_message.edit(content=new_message)

            if before.name != after.name:
                await thread.edit(
                    name=after.name,
                    reason='Associated event updated'
                )

            if before.status != after.status:
                time = int(datetime.datetime.now(
                    tz=pytz.timezone('UTC')).timestamp() // 1)
                if after.status == discord.ScheduledEventStatus.active:
                    await thread.send(f'**===== EVENT STARTED <t:{time}:F> =====**')
                if after.status == discord.ScheduledEventStatus.completed:
                    await thread.send(f'**===== EVENT ENDED <t:{time}:F> =====**')
                    self.events[str(after.guild.id)].pop(str(after.id))
                    with open('persistent/events.json', 'w') as f:
                        json.dump(self.events, f)
                        f.close()

            logger.info(f'Updated forum channel post {thread.id} for scheduled '
                        f'event {after.id} [{after.name}]')
        except discord.Forbidden as err:
            logger.warning('Could not create post, Forbidden error', exc_info=err)
        except discord.HTTPException as err:
            logger.warning('Could not create post, HTTP error', exc_info=err)


def setup(bot: commands.Bot):
    bot.add_cog(EventThreads(bot))


def teardown(bot: commands.Bot):
    bot.remove_cog('EventThreads')
