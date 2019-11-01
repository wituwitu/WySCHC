from Messages import SCHC_Frag_Message
from Messages.Header import Header
from Messages.Payload import Payload


class Fragment:

    profile = None
    header_length = 0
    rule_id_size = 0
    t = 0
    n = 0
    window_size = 0

    header = None
    payload = None

    def __init__(self, profile, fragment):
        self.profile = profile

        self.header_length = profile.HEADER_LENGTH
        self.rule_id_size = profile.RULE_ID_SIZE
        self.t = profile.T
        self.n = profile.N
        self.window_size = profile.WINDOW_SIZE

        header = fragment[:self.header_length]
        payload = fragment[self.header_length:]

        rule_id = header[:self.rule_id_size]
        dtag = header[self.rule_id_size:self.rule_id_size + self.t]
        window = header[self.rule_id_size + self.t:self.rule_id_size + self.t + self.window_size]
        fcn = header[self.rule_id_size + self.t + self.window_size:self.rule_id_size + self.t + self.window_size + self.n]
        c = ""

        self.header = Header(self.profile, rule_id, dtag, window, fcn, c)
        self.payload = Payload(self.profile, payload)

