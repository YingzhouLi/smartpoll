class Option:
    number: int
    content: str
    votes: list

    def __init__(self, number: int, content: str):
        self.number = int(number),
        self.content = content
        self.votes = []

    def __str__(self):
        return f"ID: {self.number}\n{self.content}\n{self.votes}"


class Poll:
    exists: bool
    id: int
    question: str
    creator: str

    def __init__(self, poll_id: int, question: str, creator: str):
        self.exists = poll_id is not None
        self.id = poll_id
        self.question = question
        self.creator = creator
