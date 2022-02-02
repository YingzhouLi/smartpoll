import random
import string

from sqlalchemy import Table, MetaData, Column
from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy.engine import Engine

from .types import Poll


def _generate_random_string() -> str:
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase \
            + string.digits) for _ in range(6))


class PollDatabase:
    db: Engine
    polls: Table
    options: Table
    votes: Table

    def __init__(self, db: Engine):
        self.db = db

        meta = MetaData()
        meta.bind = db
        self.polls = Table("polls", meta,
                         Column("id", Integer, primary_key=True,
                             autoincrement=True),
                         Column("code", String(6), nullable=False),
                         Column("creator", String(255), nullable=False),
                         Column("room_id", String(255), nullable=False),
                         Column("create_time", DateTime, nullable=False),
                         Column("question", Text, nullable=False),
                         Column("close_time", DateTime, nullable=True))

        self.options = Table("options", meta,
                           Column("id", Integer, primary_key=True,
                               autoincrement=True),
                           Column("poll_id", Integer, nullable=False),
                           Column("option_idx", Integer, nullable=False),
                           Column("content", Text, nullable=False))

        self.votes = Table("votes", meta,
                         Column("id", Integer, primary_key=True,
                             autoincrement=True),
                         Column("poll_id", Integer, nullable=False),
                         Column("option_id", Integer, nullable=False),
                         Column("voter", String(255), nullable=False),
                         Column("time", DateTime, nullable=False))
        meta.create_all()

    def create_poll(self,
            question: str, options: list, creator: str, room_id: str
            ) -> str:
        code = _generate_random_string()
        proxy = self.db.execute(
            self.polls.insert().values(code=code, creator=creator,
                question=question, room_id=room_id)
            )
        for index, option in enumerate(options):
            self.db.execute(
                self.options.insert().values(
                    poll_id=proxy.inserted_primary_key[0],
                    option_idx=index + 1, content=option))
        return code

    def get_poll(self, room_id: str, code: str):
        poll = self.db.execute(
            self.polls.select().where(
                self.polls.c.room_id == room_id).where(
                    self.polls.c.code == code)).fetchone()
        if poll is None:
            return Poll(None, None, None)
        return Poll(poll.id, poll.question, poll.creator)

    def get_poll_options_ids(self, poll_id: int):
        proxy = self.db.execute(self.options.select().where(
            self.options.c.poll_id == poll_id))
        options = {}
        for row in proxy:
            options[row.option_idx] = row.id
        return options

    def get_poll_options(self, poll_id: int):
        return self.db.execute(self.options.select().where(
            self.options.c.poll_id == poll_id))

    def set_vote(self, poll_id: int, option_id: int, user_id: str):
        self.db.execute(
            self.votes.delete().where(
                self.votes.c.poll_id == poll_id).where(
                    self.votes.c.voter == user_id))
        self.db.execute(self.votes.insert().values(poll_id=poll_id,
            option_id=option_id, voter=user_id))

    def get_votes(self, poll_id: int):
        return self.db.execute(self.votes.select().where(
            self.votes.c.poll_id == poll_id)).fetchall()
