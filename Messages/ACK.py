class ACK:

    profile = None
    rule_id = None
    dtag = None
    w = None
    bitmap = None
    c = None
    header = ''
    padding = ''

    def __init__(self, profile, rule_id, dtag, w, bitmap, c):
        self.profile = profile
        # self.header = Header(profile, message.header.RULE_ID, message.header.DTAG.zfill(2), message.header.W[-1],
        # fcn="", c="0")		# [-1]: the least significant bit

        self.rule_id = rule_id
        self.dtag = dtag
        self.w = w
        self.bitmap = bitmap
        self.c = c

        self.header = self.rule_id + self.dtag + self.w + self.bitmap + self.c

        print("Applying padding for ACK...")
        while len(self.header + self.padding) < profile.MTU:
            self.padding += "X"

        print("ACK is now " + str(len(self.header + self.padding)) + " bits long")

    def to_string(self):
        return self.header + self.padding
