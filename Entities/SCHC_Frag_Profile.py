class SCHCFragProfile:
    MAX_PACKET_SIZE = None              # maximum packet size that should ever be reconstructed by SCHC Decompression
    L2_WORD_SIZE = None                 # layer 2 word size in bits
    T = None                            # presence and number of bits for DTag (dtag_size)
    WINDOW_SIZE = None                  # for modes that use windows
    M = None                            # number of bits for W (w_size)
    N = None                            # number of bits for FCN (fcn_size)
    RCS_SIZE = None                     # size of RCS
    RCS_ALGORITHM = None                # alg. for RCS computation (default CRC32)
    RETRANSMISSION_TIMER_VALUE = None   # retransmission timer duration for F/R
    INACTIVITY_TIMER_VALUE = None       # inactivity timer duration for F/R
    MAX_ACK_REQUEST = None              # value for F/R
    MIN_TILE_SIZE = None
    TILE_SIZE = None
    DIRECTION = None
    PROTOCOL = None
    PADDING_BITS = None                 # 0 or 1
    SCHC_BYTES_LEN = None

    def __init__(self, protocol, direction, schc_packet):
        self.PROTOCOL = protocol
        self.SCHC_BYTES_LEN = len(schc_packet)
        self.direction = direction

        self.L2_WORD_SIZE = protocol.get_L2_WORD_SIZE(direction)
        self.TILE_SIZE = protocol.get_TILE_SIZE(direction)

        self.M = protocol.get_M(direction, self.SCHC_BYTES_LEN)

        self.N = protocol.get_N(direction)

        self.WINDOW_SIZE = protocol.get_WINDOW_SIZE(direction)

        if self.WINDOW_SIZE > 2 ** self.N:
            print("ERROR: WINDOW_SIZE can not be greater than 2^N")

        self.RCS_SIZE = protocol.get_RCS_SIZE(direction)
        self.RCS_ALGORITHM = protocol.get_RCS_ALGORITHM(direction)

        self.T = protocol.get_T(direction)

        self.MAX_ACK_REQUEST = protocol.get_MAX_ACK_REQUESTS(direction)

        self.RETRANSMISSION_TIMER_VALUE = protocol.get_RETRANSMISSION_TIMER_VALUE(direction)

        self.INACTIVITY_TIMER_VALUE = protocol.get_INACTIVITY_TIMER_VALUE(direction)
