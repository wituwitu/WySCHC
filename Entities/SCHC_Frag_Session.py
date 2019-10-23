from Entities import SCHC_Frag_Profile
from Messages import SCHC_Frag_Message


class SCHC_Frag_Session:

	RULE_ID = None
	DTAG = None
	PROFILE = None
	ATTEMPTS_COUNTER = None
	SCHC_PACKET = None
	SCHC_PACKET_REST = None
	TILES_BUFFER = {}
	TILES_COUNTER = 1

	def __init__(self, profile, schc_packet):
		self.PROFILE = profile
		self.SCHC_PACKET = list(schc_packet)

		m = profile.M
		window_size = profile.WINDOW_SIZE
		schc_packet_bytes_length = profile.SCHC_PACKET_BYTES_LENGTH

		if schc_packet_bytes_length < (2 ** m) * window_size:
			print("ERROR: A Rule MUST NOT be selected if the values of M and WINDOW_SIZE for that Rule are such that "
				  "the SCHC Packet cannot be fragmented in (2^M) * WINDOW_SIZE tiles or less.")

		self.ATTEMPTS_COUNTER = 0