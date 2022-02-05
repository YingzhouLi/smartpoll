import re

from mautrix.types import EventType, ReactionEvent, RedactionEvent
from maubot import Plugin, MessageEvent
from maubot.handlers import command

from .database import PollDatabase
from .classes import Poll

EMOJI_LIST = ["\u0031\uFE0F\u20E3", "\u0032\uFE0F\u20E3", "\u0033\uFE0F\u20E3",
              "\u0034\uFE0F\u20E3", "\u0035\uFE0F\u20E3", "\u0036\uFE0F\u20E3",
              "\u0037\uFE0F\u20E3", "\u0038\uFE0F\u20E3", "\u0039\uFE0F\u20E3",
              "\U0001F51F"]
EMOJI_REGEX = r"^[\u0031-\u0040\U0001F51F]"


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
                    for poll in self.current_polls[evt.room_id]:
                        if event_id == poll.event_id:
                            await evt.client.redact(
                                evt.room_id, poll.poll_event_id)
                            poll.renew(question, choices)
                            poll.poll_event_id = await self.client.send_text(
                                evt.room_id,
                                poll.generate_poll_text_message(),
                                poll.generate_poll_html_message())
                            for it in range(len(choices)):
                                await evt.client.react(
                                    evt.room_id, poll.poll_event_id,
                                    EMOJI_LIST[it])
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
            except ValueError:
                return

            try:
                self.current_polls[evt.room_id][idx].vote(choice_idx,
                                                    evt.sender, evt.event_id)
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

    #@poll_command.subcommand(
    #        name="ping", help="Pings the participants of a poll " \
    #                            "who voted for the specified choice.")
    #@command.argument(
    #        name="code", label="Code", pass_raw=False, required=True)
    #@command.argument(
    #        name="choice", label="Choice", pass_raw=False, required=True)
    #async def ping_poll(self, evt: MessageEvent, code: str, choice: str):
    #    poll = self.db.get_poll(evt.room_id, code)
    #    if not poll.exists:
    #        await self._send_temporary_response(
    #                "This poll does not exist!", evt)
    #        return
    #    if poll.creator.strip() != evt.sender.strip():
    #        await self._send_temporary_response(
    #                "Only the creator of the poll can ping participants!",
    #                evt)
    #        return
    #    try:
    #        opt = int(choice)
    #        choices = self._sort_choices(poll.id)[1]
    #        for choice in choices:
    #            if choice.number[0] == opt:
    #                msg = f"**Choice {opt}:** *{choice.content}* \n\n"
    #                for vote in choice.votes:
    #                    msg = msg + f"{vote}, "
    #                await evt.respond(_remove_suffix(msg, ", "))
    #                return
    #        raise ValueError
    #    except ValueError:
    #        await self._send_temporary_response(
    #                "You must specify a valid choice!", evt)