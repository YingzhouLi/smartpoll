import random
import string
from datetime import datetime

def _generate_random_string() -> str:
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase \
            + string.digits) for _ in range(6))


class Choice:
    poll_event_id: int
    poll_code:     int
    index:         int
    content:       str

    def __init__(self, poll, index, content):
        self.poll_event_id = poll.event_id
        self.poll_code     = poll.code
        self.index         = index
        self.content       = content


class Vote:
    choice_index:  int
    num_vote:      int
    voters:        list
    voters_disp:   list
    timestamp:     list

    def __init__(self, choice_index):
        self.choice_index = choice_index
        self.num_vote     = 0
        self.voters       = []
        self.voters_disp  = []
        self.timestamp    = []

    def vote(self, voter, voter_disp):
        if voter in self.voters:
            return 0
        else:
            self.num_vote += 1
            self.voters.append(voter)
            self.voters_disp.append(voter_disp)
            self.timestamp.append(datetime.now())
            return 1

    def recall_vote(self, voter): # Return whether successfully recalled
        if voter in self.voters:
            self.num_vote -= 1
            idx = self.voters.index(voter)
            del self.voters[idx]
            del self.voters_disp[idx]
            del self.timestamp[idx]
            return 1
        else:
            return 0


class Poll:
    event_id:       str
    poll_event_id:  str
    room_id:        str
    code:           str
    timestamp:      datetime
    creator:        str
    question:       str
    choices:        list
    votes:          list
    event_ids:      list
    voters:         list
    choice_indices: list
    totalvotes:     int
    mcp:            bool # Multiple-Choice Poll
                         # if true, only one choice can be selected

    def __init__(self, event_id, room_id, creator, question, choices,
            mcp = False):
        self.event_id       = event_id
        self.room_id        = room_id
        self.code           = _generate_random_string() 
        self.timestamp      = datetime.now()
        self.creator        = creator.strip()
        self.question       = question
        self.totalvotes     = 0
        self.mcp            = mcp
        self.votes          = []
        self.choices        = []
        self.event_ids      = []
        self.voters         = []
        self.choice_indices = []
        for index, content in enumerate(choices):
            self.choices.append(Choice(self, index, content))
            self.votes.append(Vote(index))

    def renew(self, question, choices, mcp = False):
        self.timestamp      = datetime.now()
        self.question       = question
        self.totalvotes     = 0
        self.mcp            = mcp
        self.votes          = []
        self.choices        = []
        self.event_ids      = []
        self.voters         = []
        self.choice_indices = []
        for index, content in enumerate(choices):
            self.choices.append(Choice(self, index, content))
            self.votes.append(Vote(index))

    def vote(self, choice_index, voter, voter_disp, vote_event_id):
        if self.mcp:
            if voter in self.voters:
                raise Exception("Only one choice can be choosen.")
            else:
                self.votes[choice_index].vote(voter, voter_disp)
                self.totalvotes += 1
                self.event_ids.append(vote_event_id)
                self.voters.append(voter)
                self.choice_indices.append(choice_index)
        else:
            cnt = self.votes[choice_index].vote(voter, voter_disp)
            self.totalvotes += cnt
            if cnt == 0:
                raise Exception("A voter can only vote for a choice once.")
            else:
                self.event_ids.append(vote_event_id)
                self.voters.append(voter)
                self.choice_indices.append(choice_index)

    def recall_vote(self, vote_event_id):
        if vote_event_id in self.event_ids:
            idx = self.event_ids.index(vote_event_id)
            choice_index = self.choice_indices[idx]
            voter = self.voters[idx]
            cnt = self.votes[choice_index].recall_vote(voter)
            self.totalvotes -= cnt
            if cnt == 0:
                raise Exception("No vote found for the voter.")
            else:
                del self.event_ids[idx]
                del self.choice_indices[idx]
                del self.voters[idx]
        else:
            raise Exception("No vote found for the voter.")

    def generate_poll_html_message(self):
        message = f"<h4><em>{self.question}</em></h4>\n"
        message += "<ol>\n"
        for choice in self.choices:
            message += f"<li>{choice.content}</li>\n"
        message += "\n</ol>\n"

        message += "<p><em>Poll code: </em>" \
                + f"<code>{self.code}</code></p>"
        return message

    def generate_poll_text_message(self):
        message = f"#### {self.question}\n"
        for choice in self.choices:
            message += f"{choice.index+1}. {choice.content}\n"
        message += f"\n Poll code: `{self.code}`\n"
        return message

    def generate_result_html_message(self):
        message = f"<h4>Poll result: <em>{self.question}</em></h4><ol>"
        for it in range(len(self.choices)):
            message += f"<li>{self.choices[it].content}<br>"
            message += f"<em>{self.votes[it].num_vote} in {self.totalvotes}" \
                f" Votes - "\
                f"{'{:.0%}'.format(self.votes[it].num_vote / max(1,self.totalvotes))}" \
                f"</em></li>"
        return message + "</ol>"

    def generate_result_text_message(self):
        message = f"#### Poll result: **{self.question}**\n"
        for it in range(len(self.choices)):
            message += f"{self.choices[it].index+1}. "\
                f"{self.choices[it].content}\n"
            message += f"{self.votes[it].num_vote} in {self.totalvotes}" \
                f" Votes - "\
                f"{'{:.0%}'.format(self.votes[it].num_vote / max(1,self.totalvotes))}\n"
        return message

    def generate_ping_html_message(self, choice_index):
        if choice_index > len(self.choices):
            message = "<p>Invalid choice index!</p>\n"
            return message
        message = f"<h4>Poll ping: <em>{self.question}</em></h4>\n"
        message += f"<h5>Voters for choice {choice_index}: "
        message += f"{self.choices[choice_index-1].content}</h5>\n<ol>"
        for it in range(len(self.votes[choice_index-1].voters)):
            voter = self.votes[choice_index-1].voters[it]
            voterdisp = self.votes[choice_index-1].voters_disp[it]
            message += f"<li> <a href=\"https://matrix.to/#/{voter}\">"
            message += f"{voterdisp}</a></li>"
        return message + "</ol>"

    def generate_ping_text_message(self, choice_index):
        if choice_index > len(self.choices):
            message = "Invalid choice index!\n"
            return message
        message = f"#### Poll ping: **{self.question}**\n\n"
        message += f"##### Voters for choice {choice_index}: "
        message += f"{self.choices[choice_index-1].content}\n"
        for it in range(len(self.votes[choice_index-1].voters)):
            voterdisp = self.votes[choice_index-1].voters_disp[it]
            message += f"{it+1}. {voterdisp}\n"
        return message
