# coding: utf-8
from datetime import date, datetime

from message import Message 

class BotResponse:
    def __init__(self):
        self.messages = []

    def add_message(self, new_message):
        self.messages.append(new_message)

    def asdict(self):
        for i in range(len(self.messages)):
            self.messages[i] = self.messages[i].asdict()
        return {"messages": self.messages}