# coding: utf-8
from unstructured_message import UnstructuredMessage  # noqa: F401,E501

class Message:
    def __init__(self, type, text):
        assert(isinstance(type, str))
        assert(isinstance(text, str))
        self.type = type
        self.unstructured = UnstructuredMessage("01", text)

    def asdict(self):
        return {"type": self.type, "unstructured": self.unstructured.asdict()}