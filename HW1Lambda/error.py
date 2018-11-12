# coding: utf-8
class Error:
    def __init__(self, code, message):
        assert(isinstance(message, str))
        assert(isinstance(code, int))
        self.code = code
        self.message = message

    def asdict(self):
        return {"code": self.code, "message": self.message}