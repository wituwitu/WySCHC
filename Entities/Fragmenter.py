from math import ceil, floor

from Messages.Header import Header


class Fragmenter:
	profile = None
	schc_packet = None

	def __init__(self, profile, schc_packet):
		self.profile = profile
		self.schc_packet = schc_packet

	def fragment(self):
		payload_max_length = 14 - self.profile.HEADER_LENGTH  # self.profile.MTU - header_length
		message = self.schc_packet
		fragment_list = []
		n = self.profile.N
		window_size = self.profile.WINDOW_SIZE

		number_of_fragments = ceil(len(message) / payload_max_length)

		print("Fragmenting message into " + str(number_of_fragments) + " pieces...")

		for i in range(number_of_fragments):
			print("Fragment number " + str(i))

			w = bin(floor((i/(2**n - 1) % (2**window_size))))[2:].zfill(2)
			fcn = bin((2 ** n - 2) - (i % (2 ** n - 1)))[2:].zfill(3)

			fragment_payload = message[i * payload_max_length:(i + 1) * payload_max_length]

			if len(fragment_payload) < payload_max_length:
				header = Header(self.profile, rule_id="RR", dtag="D", w=w, fcn="111", c=0)
				print("Applying padding for final fragment...")
				while len(fragment_payload) < payload_max_length:
					fragment_payload += "X"

			else:
				header = Header(self.profile, rule_id="RR", dtag="D", w=w, fcn=fcn, c=0)


			fragment = header.STRING + fragment_payload
			print("[" + header.STRING + "]" + fragment_payload)
			fragment_list.append(fragment)

		print("Fragmentation complete.")

		return fragment_list
