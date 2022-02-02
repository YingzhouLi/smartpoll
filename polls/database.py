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
    choices: Table
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
                         Column("question", Text, nullable=False),
                         Column("create_time", DateTime, nullable=False),
                         Column("close_time", DateTime, nullable=True))

        self.options = Table("options", meta,
                           Column("id", Integer, primary_key=True,
                               autoincrement=True),
                           Column("poll_id", Integer, nullable=False),
                           Column("option_number", Integer, nullable=False),
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
            question: str, choices: list, creator: str, room_id: str
            ) -> str:
        code = _generate_random_string()
        proxy = self.db.execute(
            self.polls.insert().values(code=code, creator=creator,
                question=question, room_id=room_id)
            )
        for index, choice in enumerate(choices):
            self.db.execute(
                self.choices.insert().values(
                    poll_id=proxy.inserted_primary_key[0],
                    choice_number=index + 1, content=choice))
        return code

    def get_poll(self, room_id: str, code: str):
        poll = self.db.execute(
            self.polls.select().where(
                self.polls.c.room_id == room_id).where(
                    self.polls.c.code == code)).fetchone()
        if poll is None:
            return Poll(None, None, None)
        return Poll(poll.id, poll.question, poll.creator)

    def get_poll_choices_ids(self, poll_id: int):
        proxy = self.db.execute(self.choices.select().where(
            self.choices.c.poll_id == poll_id))
        choices = {}
        for row in proxy:
            choices[row.choice_number] = row.id
        return choices

    def get_poll_choices(self, poll_id: int):
        return self.db.execute(self.choices.select().where(
            self.choices.c.poll_id == poll_id))

    def set_vote(self, poll_id: int, choice_id: int, user_id: str):
        self.db.execute(
            self.votes.delete().where(
                self.votes.c.poll_id == poll_id).where(
                    self.votes.c.voter == user_id))
        self.db.execute(self.votes.insert().values(poll_id=poll_id,
            choice_id=choice_id, voter=user_id))

    def get_votes(self, poll_id: int):
        return self.db.execute(self.votes.select().where(
            self.votes.c.poll_id == poll_id)).fetchall()
