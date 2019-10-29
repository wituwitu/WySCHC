from Messages.Fragment import Fragment
from anytree import Node


class Reassembler:
	profile = None
	schc_fragments = []
	rule_set = set()
	dtag_set = set()
	window_set = set()
	fcn_set = set()

	def __init__(self, profile, schc_fragments):
		self.profile = profile

		for fragment in schc_fragments:
			self.schc_fragments.append(Fragment(self.profile, fragment))

		for fragment in self.schc_fragments:
			self.rule_set.add(fragment.header.RULE_ID)
			self.dtag_set.add(fragment.header.DTAG)
			self.window_set.add(fragment.header.W)
			self.fcn_set.add(fragment.header.FCN)

	# def order_by_rule(self):
	# 	fragment_list = []
	# 	for rule in self.rule_set:
	# 		for fragment in self.schc_fragments:
	# 			if rule == fragment.header.RULE_ID:
	# 				fragment_list.append(fragment)
	# 	self.schc_fragments = fragment_list
	#
	# def order_by_dtag(self):
	# 	fragment_list = []
	# 	for rule in self.rule_set:
	# 		for dtag in self.dtag_set:
	# 			for fragment in self.schc_fragments:
	# 				if rule == fragment.header.RULE_ID and dtag == fragment.header.DTAG:
	# 					fragment_list.append(fragment)
	# 	self.schc_fragments = fragment_list
	#
	# def order_fragments(self):
	# 	fragment_list = []
	# 	for rule in self.rule_set:
	# 		for dtag in self.dtag_set:
	# 			for window in self.window_set:
	# 				for fcn in self.fcn_set:
	# 					for fragment in self.schc_fragments:
	# 						header = fragment.header
	# 						if rule == header.RULE_ID and dtag == header.DTAG and window == header.W and fcn =
	# 							fragment_list.append(fragment)
	# 		self.schc_fragments = fragment_list

	def reassemble(self):
		message = None

		header_length = self.profile.HEADER_LENGTH
		rule_id_size = self.profile.RULE_ID_SIZE
		t = self.profile.T
		n = self.profile.N
		window_size = self.profile.WINDOW_SIZE

		payload_max_length = 14 - header_length  # self.profile.MTU - header_length
		fragments = self.schc_fragments
		fragment_list = []
		payload_list = []

		# TODO: ORDER FRAGMENTS (commented)
		# they recommended me to use an R-tree data structure but the name scares me a lot

		# assuming all fragments are ordered properly, the only thing that's left is joining the payloads
		# self.schc_fragments MUST HAVE BEEN ORDERED

		for fragment in fragments:
			payload_list.append(fragment.payload.payload)

		return "".join(payload_list)

	# ABOUT PADDING BITS:
	# The "Static Context Header Compression (SCHC) and fragmentation for LPWAN, application to UDP/IPv6" draft says:
	# "the full SCHC
	# Fragment Payload MUST be assembled including the padding bits.
	# This is because the size of the last tile is not known by the
	# receiver, therefore padding bits are indistinguishable from the
	# tile data bits, at this stage.  They will be removed by the SCHC
	# C/D sublayer."
