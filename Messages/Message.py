from Messages import Header
from Messages import Payload

class Message:
    header = None
    payload = None

    def __init__(self, header, payload):
        self.header = header
        self.payload = payload
        pass
