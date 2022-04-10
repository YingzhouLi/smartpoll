import re

from mautrix.types import EventType, ReactionEvent, RedactionEvent
from maubot import Plugin, MessageEvent
from maubot.handlers import command

from .database import PollDatabase
from .classes import Poll

EMOJI_LIST = ["\u0031\uFE0F\u20E3", "\u0032\uFE0F\u20E3", "\u0033\uFE0F\u20E3",
              "\u0034\uFE0F\u20E3", "\u0035\uFE0F\u20E3", "\u0036\uFE0F\u20E3",
              "\u0037\uFE0F\u20E3", "\u0038\uFE0F\u20E3", "\u0039\uFE0F\u20E3",
              "\U0001F51F",
              "\U0001F1E6", "\U0001F1E7", "\U0001F1E8", "\U0001F1E9",
              "\U0001F1EA", "\U0001F1EB", "\U0001F1EC", "\U0001F1ED",
              "\U0001F1EE", "\U0001F1EF", "\U0001F1F0", "\U0001F1F1",
              "\U0001F1F2", "\U0001F1F3", "\U0001F1F4", "\U0001F1F5",
              "\U0001F1F6", "\U0001F1F7", "\U0001F1F8", "\U0001F1F9",
              "\U0001F1FA", "\U0001F1FB", "\U0001F1FC", "\U0001F1FD",
              "\U0001F1FE", "\U0001F1FF"]
EMOJI_REGEX = r"^[\u0031-\u0040\U0001F51F\U0001F1E6-\U0001F200]"


class SmartPoll(Plugin):
    db:             PollDatabase
    current_polls:  dict
    current_events: dict
    current_codes:  dict

    async def start(self) -> None:
        self.current_polls = {}
        self.current_events = {}
        self.current_codes = {}
        #self.db = PollDatabase(self.database)

    @command.new(name="poll", require_subcommand=True)
    async def poll(self):
        pass

    @poll.subcommand(name="create", aliases=["new"], 
            help="Create a new poll: " \
                "`!poll create <Question> | <Choice 1> | <Choice 2> ...`")
    @command.argument("poll_setup", pass_raw=True, required=True)
    async def create_poll(self, evt: MessageEvent, poll_setup):
        if poll_setup is not "":
            raw_parts = re.split('\||\n', poll_setup)
            if len(raw_parts) < 3:
                await evt.reply("Please provide at least 2 choices.")
            else:
                question = raw_parts[0]
                choices = raw_parts[1:]
                # make an empty list if no polls in current room
                if not self.current_polls.get(evt.room_id, False):
                    self.current_polls[evt.room_id] = []
                    self.current_events[evt.room_id] = []
                    self.current_codes[evt.room_id] = []

                if evt.content.relates_to.event_id is not None:
                    event_id = evt.content.relates_to.event_id
                    for idx, poll in enumerate(self.current_polls[evt.room_id]):
                        if event_id == poll.event_id:
                            await evt.client.redact(
                                evt.room_id, poll.poll_event_id)
                            poll.renew(question, choices)
                            poll.poll_event_id = await self.client.send_text(
                                evt.room_id,
                                poll.generate_poll_text_message(),
                                poll.generate_poll_html_message())
                            if len(choices) > 10:
                                for it in range(len(choices)):
                                    await evt.client.react(
                                        evt.room_id, poll.poll_event_id,
                                        EMOJI_LIST[it+10])
                            else:
                                for it in range(len(choices)):
                                    await evt.client.react(
                                        evt.room_id, poll.poll_event_id,
                                        EMOJI_LIST[it])
                            self.current_events[evt.room_id][idx] = \
                                poll.poll_event_id
                            return

                newpoll = Poll(evt.event_id, evt.room_id, evt.sender,
                            question, choices)
                self.current_polls[evt.room_id].append(newpoll)
                
                newpoll.poll_event_id = await self.client.send_text(
                    evt.room_id,
                    newpoll.generate_poll_text_message(),
                    newpoll.generate_poll_html_message())
                self.current_events[evt.room_id].append(newpoll.poll_event_id)
                self.current_codes[evt.room_id].append(newpoll.code)

                if len(choices) > 10:
                    for it in range(len(choices)):
                        await evt.client.react(
                            evt.room_id, newpoll.poll_event_id,
                            EMOJI_LIST[it+10])
                else:
                    for it in range(len(choices)):
                        await evt.client.react(
                            evt.room_id, newpoll.poll_event_id, EMOJI_LIST[it])
        else:
            await evt.reply("Invalid input! Please check `!poll` for help.")

    @poll.subcommand(name="result", aliases=["print"], 
            help="Print the result of a poll: " \
                "`!poll result <Code>`")
    @command.argument("code", pass_raw=False, required=True)
    async def poll_result(self, evt: MessageEvent, code):
        try:
            idx = self.current_codes[evt.room_id].index(code)
        except ValueError:
            await evt.reply("The poll code does not exist.")
            return
        if self.current_polls[evt.room_id][idx].creator != evt.sender.strip():
            await evt.reply("Only the creator can show the result.")
            return
        await self.client.send_text(evt.room_id,
            self.current_polls[evt.room_id][idx].generate_result_text_message(),
            self.current_polls[evt.room_id][idx].generate_result_html_message())

    @poll.subcommand(
            name="ping", help="Pings the voters for the choice.")
    @command.argument(
            name="code", label="Code", pass_raw=False, required=True)
    @command.argument(
            name="choice", label="Choice", pass_raw=False, required=True)
    async def poll_ping(self, evt: MessageEvent, code, choice):
        try:
            idx = self.current_codes[evt.room_id].index(code)
        except ValueError:
            await evt.reply("The poll code does not exist.")
            return
        if self.current_polls[evt.room_id][idx].creator != evt.sender.strip():
            await evt.reply("Only the creator can show the result.")
            return
        try:
            if choice >= 'A' and choice <= "Z":
                choice_index = ord(choice) - 64
            else:
                choice_index = int(choice)
        except:
            await evt.reply("Invalid choice index!")
            return
        await self.client.send_text(evt.room_id,
            self.current_polls[evt.room_id][idx].generate_ping_text_message(
                choice_index),
            self.current_polls[evt.room_id][idx].generate_ping_html_message(
                choice_index))
        
    @poll.subcommand(name="close", aliases=["delete"], 
            help="Close a poll: " \
                "`!poll close <Code>`")
    @command.argument("code", pass_raw=False, required=True)
    async def poll_close(self, evt: MessageEvent, code):
        try:
            idx = self.current_codes[evt.room_id].index(code)
        except ValueError:
            await evt.reply("The poll code does not exist.")
            return
        if self.current_polls[evt.room_id][idx].creator != evt.sender.strip():
            await evt.reply("Only the creator can close the poll.")
            return
        del self.current_polls[evt.room_id][idx]
        del self.current_codes[evt.room_id][idx]
        del self.current_events[evt.room_id][idx]
        await evt.reply("The poll has been closed.")
    
    @command.passive(regex=EMOJI_REGEX,
                     field=lambda evt: evt.content.relates_to.key,
                     event_type=EventType.REACTION, msgtypes=None)
    async def get_react_vote(self, evt: ReactionEvent, _):
        event_id = evt.content.relates_to.event_id
        emoji    = evt.content.relates_to.key
        if event_id in self.current_events[evt.room_id]:
            idx = self.current_events[evt.room_id].index(event_id)
            try:
                choice_idx = EMOJI_LIST.index(emoji)
                if len(self.current_polls[evt.room_id][idx].choices) > 10:
                    choice_idx -= 10
            except ValueError:
                return

            try:
                voterdisp = await self.client.get_displayname(evt.sender)
                self.current_polls[evt.room_id][idx].vote(choice_idx,
                                                    evt.sender, voterdisp,
                                                    evt.event_id)
            except Exception as errmsg:
                self.log.info(errmsg)

    @command.passive(regex=r"",
                     field=lambda evt: evt.event_id,
                     event_type=EventType.ROOM_REDACTION, msgtypes=None)
    async def get_redact_vote(self, evt: RedactionEvent, _):
        event_id = evt.redacts
        for poll in self.current_polls[evt.room_id]:
            if event_id in poll.event_ids:
                try:
                    poll.recall_vote(event_id)
                except Exception as errmsg:
                    self.log.info(errmsg)

