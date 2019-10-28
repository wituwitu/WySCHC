from Messages.Fragment import Fragment
from anytree import Node


class Reassembler:
	profile = None
	schc_fragments = None

	def __init__(self, profile, schc_fragments):
		self.profile = profile
		self.schc_fragments = schc_fragments

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

		# TODO: Order fragments
		# TODO: Check rule ID

		for fragment in fragments:
			fragment_list.append(Fragment(self.profile, fragment))

		rule_set = set()
		dtag_set = set()
		window_set = set()
		fcn_set = set()

		for fragment in fragment_list:
			rule_set.add(fragment.header.RULE_ID)
			dtag_set.add(fragment.header.DTAG)
			window_set.add(fragment.header.W)
			fcn_set.add(fragment.header.FCN)

		for fragment in fragment_list:
			for rule in rule_set:
				rule_node = Node(rule)
				for dtag in dtag_set:
					dtag_node = Node(dtag, parent=rule_node)
					for window in window_set:
						window_node = Node(window, parent=dtag_node)
						for fcn in fcn_set:
							fcn_node = Node(fragment, parent=window_node)


