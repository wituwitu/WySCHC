from Entities.Protocol import Protocol

# Glossary
# T: DTag size
# N: Fragment Compressed Number (FCN) size
# M: Window identifier (present only if windows are used) size
# U: Reassembly Check Sequence (RCS) size


class Sigfox(Protocol):

	direction = None
	mode = None

	def __init__(self, direction, mode):

		print("This protocol is in " + direction + " direction and " + mode + " mode.")

		self.NAME = "SIGFOX"
		self.DIRECTION = direction
		self.MODE = mode
		self.RETRANSMISSION_TIMER_VALUE = 45
		self.INACTIVITY_TIMER_VALUE = 45

		self.N = 0

		self.HEADER_LENGTH = 0

		self.MESSAGE_INTEGRITY_CHECK_SIZE = None  # TBD
		self.RCS_ALGORITHM = None  # TBD

		if direction == "UPLINK":
			self.MTU = 12*8

			if mode == "NO ACK":
				self.HEADER_LENGTH = 8
				self.RULE_ID_SIZE = 2			# recommended
				self.T = 2						# recommended
				self.N = 4						# recommended
				self.WINDOW_SIZE = 0

			if mode == "ACK ALWAYS":
				pass							# TBD

			if mode == "ACK ON ERROR":
				self.HEADER_LENGTH = 8
				self.RULE_ID_SIZE = 2
				self.T = 1
				self.N = 3
				self.WINDOW_SIZE = 2			# recommended to be single  (what does this mean?)
				self.MAX_ACK_REQUESTS = 2		# SHOULD be
				self.MAX_WIND_FCN = 6			# SHOULD be

		if direction == "DOWNLINK":
			self.MTU = 8*8
			self.HEADER_LENGTH = 8
			if mode == "ACK ALWAYS":
				self.RULE_ID_SIZE = 2			# recommended
				self.T = 2						# recommended
				self.N = 3						# recommended
				self.WINDOW_SIZE = 1			# MUST be present, recommended to be single (what does this mean?)
				self.MAX_ACK_REQUESTS = 2		# SHOULD be
				self.MAX_WIND_FCN = 6			# SHOULD be

				# Sigfox downlink frames have a fixed length of 8 bytes, which means
				#    that default SCHC algorithm for padding cannot be used.  Therefore,
				#    the 3 last bits of the fragmentation header are used to indicate in
				#    bytes the size of the padding.  A size of 000 means that the full
				#    ramaining frame is used to carry payload, a value of 001 indicates
				#    that the last byte contains padding, and so on.

			else:
				pass

		print("-----VALUES-----")
		print("RULE_ID_SIZE = " + str(self.RULE_ID_SIZE))
		print("T = " + str(self.T))
		print("N = " + str(self.N))
		print("WINDOW_SIZE = " + str(self.WINDOW_SIZE))
		print("MAX_ACK_REQUESTS = " + str(self.MAX_ACK_REQUESTS))
		print("MAX_WIND_FCN = " + str(self.MAX_WIND_FCN))
		print("")
		print("MTU = " + str(self.MTU))

		length = self.RULE_ID_SIZE + self.T + self.N + self.WINDOW_SIZE

		print("All headers should be " + str(length) + " bits long (" + str(length/8) + " bytes).")
