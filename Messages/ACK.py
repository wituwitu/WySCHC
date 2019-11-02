from Messages.Header import Header


class ACK:

    profile = None
    header = None
    payload = ""

    def __init__(self, profile, message):
        self.profile = profile
        # self.header = Header(profile, message.header.RULE_ID, message.header.DTAG.zfill(2), message.header.W[-1],
        # fcn="", c="0")		# [-1]: the least significant bit
        self.header = Header(profile, message.header.RULE_ID, message.header.DTAG, message.header.W, fcn=message.header.FCN)
        # print("C: " + self.header.C)
        self.header.test()

        print("Applying padding for ACK...")
        while len(self.header.string + self.payload) < profile.MTU:
            self.payload += "X"

        print("ACK is now " + str(len(self.header.string + self.payload)) + " bits long")