# -*- coding: utf-8 -*-

from math import ceil, floor
from Messages.Header import Header


class Fragmenter:
	profile = None
	schc_packet = None

	def __init__(self, profile, schc_packet):
		self.profile = profile
		self.schc_packet = schc_packet

	def fragment(self):
		payload_max_length = int((self.profile.MTU - self.profile.HEADER_LENGTH) / 8)  # self.profile.MTU - header_length
		message = self.schc_packet
		fragment_list = []
		n = self.profile.N
		window_size = self.profile.WINDOW_SIZE

		# print(str(len(message)) + "\n" + str(payload_max_length))

		# print(str(ceil(len(message) / payload_max_length)))

		number_of_fragments = int(ceil(float(len(message)) / payload_max_length))

		print("[FRGM] Fragmenting message into " + str(number_of_fragments) + " pieces...")

		for i in range(number_of_fragments):
			# print("Fragment number " + str(i))

			w = bin(int(floor((i/(2**n - 1) % (2 ** window_size)))))[2:].zfill(2)
			fcn = bin((2 ** n - 2) - (i % (2 ** n - 1)))[2:].zfill(3)

			fragment_payload = message[i * payload_max_length:(i + 1) * payload_max_length]		# Esto no debería tener problemas ya que es un arreglo de bytes

			if len(fragment_payload) < payload_max_length:
				header = Header(self.profile, rule_id="00", dtag="0", w=w, fcn="111", c=0)
				# print("Final fragment")

			# Con Sigfox se debe simplificar la implementación, ya que solo hay un tile por fragmento. También,
			# en nuestro caso consideramos que en el UL no es necesario añadir padding bits, ya que el payload puede
			# ser de 0-12 bytes - a menos de que tu payload no este byte-aligned?

				# print("Applying padding for final fragment...")
				# while len(fragment_payload) < payload_max_length:
				# 	fragment_payload += "X"
					# Uplink frames can contain a payload size from 0 to 96 bits, that is 0
					# to 12 bytes.  The radio protocol allows sending zero bits or one
					# single bit of information for binary applications (e.g. status), or
					# an integer number of bytes.  Therefore, for 2 or more bits of payload
					# it is required to add padding to the next integer number of bytes.
					# The reason for this flexibility is to optimize transmission time and
					# hence save battery consumption at the device.

			else:
				header = Header(self.profile, rule_id="00", dtag="0", w=w, fcn=fcn, c=0)

			fragment = [header.bytes, fragment_payload]
			# print("[" + header.string + "]" + str(fragment_payload))
			fragment_list.append(fragment)

		print("[FRGM] Fragmentation complete.")

		return fragment_list
