from Entities.Protocol import Protocol


class Sigfox(Protocol):

	DIRECTION = None
	MODE = None

	def __init__(self, direction, mode):

		self.NAME = "SIGFOX"
		self.DIRECTION = direction
		self.MODE = mode

		if direction == "UPLINK":
			if mode == "NO ACK":
				self.RULE_ID_SIZE = 2			# recommended
				self.T = 2						# recommended
				self.N = 4						# recommended
				self.WINDOW_SIZE = 0
				self.MESSAGE_INTEGRITY_CHECK_SIZE = None					# TBD
				self.RCS_ALGORITHM = None		# TBD

			if mode == "ACK ALWAYS":
				pass							# TBD

			if mode == "ACK ON ERROR":
				self.RULE_ID_SIZE = 2
				self.T = 1
				self.WINDOW_SIZE = 2			# recommended to be single
				self.N = 3
				self.MAX_ACK_REQUESTS = 2		# SHOULD be
				self.MAX_WIND_FCN = 6			# SHOULD be
				self.MESSAGE_INTEGRITY_CHECK_SIZE = None  # TBD
				self.RCS_ALGORITHM = None  # TBD

		if direction == "DOWNLINK":
			if mode == "ACK ALWAYS":
				self.RULE_ID_SIZE = 2			# recommended
				self.T = 2						# recommended
				self.N = 3						# recommended
				self.WINDOW_SIZE = 1			# MUST be present, recommended to be single
				self.MAX_ACK_REQUESTS = 2		# SHOULD be
				self.MAX_WIND_FCN = 6			# SHOULD be
				self.MESSAGE_INTEGRITY_CHECK_SIZE = None 		# TBD
				self.RCS_ALGORITHM = None 		# TBD

				# Sigfox downlink frames have a fixed length of 8 bytes, which means
				#    that default SCHC algorithm for padding cannot be used.  Therefore,
				#    the 3 last bits of the fragmentation header are used to indicate in
				#    bytes the size of the padding.  A size of 000 means that the full
				#    ramaining frame is used to carry payload, a value of 001 indicates
				#    that the last byte contains padding, and so on.

			else:
				pass