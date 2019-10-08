class SCHC_Frag_Profile:

    MAX_PACKET_SIZE = None              # maximum packet size that should ever be reconstructed by SCHC Decompression
    L2_WORD_SIZE = None                 # layer 2 word size in bits
    T = None                            # presence and number of bits for DTag (dtag_size)
    WINDOW_SIZE = None                  # for modes that use windows
    M = None                            # number of bits for W (w_size)
    N = None                            # number of bits for FCN (fcn_size)
    U = None                            # size of RCS
    RCS_ALGORITHM = None                # alg. for RCS computation (default CRC32)
    RETRANSMISSION_TIMER_VALUE = None   # retransmission timer duration for F/R
    INACTIVITY_TIMER_VALUE = None       # inactivity timer duration for F/R
    MAX_ACK_REQUEST = None              # value for F/R
    MIN_TILE_SIZE = None
    TILE_SIZE = None

    DIRECTION = None
    PROTOCOL = None
    MODE = None

    PADDING_BITS = None                 # 0 or 1
    SCHC_PACKET_BYTES_LEN = None

    def __init__(self, protocol, direction, mode, schc_packet): # protocol should be initialized before as protocol(direction, mode)

        self.PROTOCOL = protocol(direction, mode)
        self.SCHC_PACKET_BYTES_LEN = len(schc_packet)
        self.DIRECTION = self.PROTOCOL.direction
        self.mode = self.PROTOCOL.mode

        self.L2_WORD_SIZE = self.PROTOCOL.L2_WORD_SIZE
        self.TILE_SIZE = self.PROTOCOL.TILE_SIZE

        self.M = self.PROTOCOL.M

        self.N = self.PROTOCOL.N

        self.WINDOW_SIZE = self.PROTOCOL.WINDOW_SIZE

        if self.WINDOW_SIZE > 2 ** self.N:
            print("ERROR: WINDOW_SIZE can not be greater than 2^N")

        self.RCS_SIZE = self.PROTOCOL.RCS_SIZE
        self.RCS_ALGORITHM = self.PROTOCOL.RCS_ALGORITHM

        self.T = self.PROTOCOL.T

        self.MAX_ACK_REQUEST = self.PROTOCOL.MAX_ACK_REQUESTS

        self.RETRANSMISSION_TIMER_VALUE = self.PROTOCOL.RETRANSMISSION_TIMER_VALUE

        self.INACTIVITY_TIMER_VALUE = self.PROTOCOL.INACTIVITY_TIMER_VALUE
