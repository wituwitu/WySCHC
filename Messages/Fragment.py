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

        # print(fragment)

        header = str(bin(int.from_bytes(fragment[0], 'little')))[2:].zfill(self.header_length)
        payload = fragment[1]

        rule_id = str(header[:self.rule_id_size])
        dtag = str(header[self.rule_id_size:self.rule_id_size + self.t])
        window = str(header[self.rule_id_size + self.t:self.rule_id_size + self.t + self.window_size])
        fcn = str(header[self.rule_id_size + self.t + self.window_size:self.rule_id_size + self.t + self.window_size + self.n])
        c = ""

        # print(rule_id)
        # print(dtag)
        # print(window)
        # print(fcn)
        # print(c)

        self.header = Header(self.profile, rule_id, dtag, window, fcn, c)

        # print(payload)
        self.payload = payload

    def test(self):
        print("Header: " + self.header.string)
        print("Payload: " + str(self.payload))

    def is_all_1(self):
        fcn = self.header.FCN
        fcn_set = set()
        for x in fcn:
            fcn_set.add(x)
        return len(fcn_set) == 1 and "1" in fcn_set

    def is_all_0(self):
        fcn = self.header.FCN
        fcn_set = set()
        for x in fcn:
            fcn_set.add(x)
        return len(fcn_set) == 1 and "0" in fcn_set
