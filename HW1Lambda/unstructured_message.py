# coding: utf-8

import datetime 

class UnstructuredMessage:
    def __init__(self, id, text):
        assert(isinstance(id, str))
        assert(isinstance(text, str))
        self.text = text
        self.id = id
        self.timestamp = datetime.datetime.now().isoformat()

    def asdict(self):
        return {"id": self.id, "text": self.text, "timestamp": self.timestamp}
