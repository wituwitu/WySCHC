def callback_data(request):

	import sys
	import os
	import json
	import base64
	import datetime
	from flask import abort
	from rfc3339 import rfc3339
	from google.cloud import storage
	from math import ceil, floor

	def upload_blob(bucket_name, blob_text, destination_blob_name):
		"""Uploads a file to the bucket."""
		storage_client = storage.Client()
		bucket = storage_client.get_bucket(bucket_name)
		blob = bucket.blob(destination_blob_name)
		blob.upload_from_string(blob_text)
		print('File uploaded to {}.'.format(destination_blob_name))
	def read_blob(bucket_name, blob_name):
		storage_client = storage.Client()
		bucket = storage_client.get_bucket(bucket_name)
		blob = bucket.get_blob(blob_name)
		return blob.download_as_string()
	def delete_blob(bucket_name, blob_name):
		storage_client = storage.Client()
		bucket = storage_client.get_bucket(bucket_name)
		blob = bucket.get_blob(blob_name)
		blob.delete()
	def exists_blob(bucket_name, blob_name):
		storage_client = storage.Client()
		bucket = storage_client.get_bucket(bucket_name)
		blob = bucket.blob(blob_name)
		return blob.exists()
	def create_folder(bucket_name, folder_name):
		storage_client = storage.Client()
		bucket = storage_client.get_bucket(bucket_name)
		blob = bucket.blob(folder_name)
		blob.upload_from_string("")
		print('Folder uploaded to {}.'.format(folder_name))
	def size_blob(bucket_name, blob_name):
		storage_client = storage.Client()
		bucket = storage_client.get_bucket(bucket_name)
		blob = bucket.blob(blob_name)
		return blob.size
	def send_ack(request, ack):
		device = request["device"]
		response_dict = {device: {'downlinkData': ack.to_bytes()}}
		response_json = json.dumps(response_dict)
		return response_json


	if request.method == 'POST':
		http_user = os.environ.get('HTTP_USER')
		http_passwd = os.environ.get('HTTP_PASSWD')
		request_user = request.authorization["username"]
		request_passwd = request.authorization["password"]

		if request_user == http_user and request_passwd == http_passwd:

			BUCKET_NAME = 'wyschc'
			request_dict = request.get_json()
			print('Received Sigfox message: {}'.format(request_dict))

			print("Loading classes...")
			#  CLASSES
			# -fragment elements
			class Header:
				profile = None

				RULE_ID = ""
				DTAG = ""
				W = ""
				FCN = ""
				C = ""

				string = ""
				bytes = None

				def __init__(self, profile, rule_id, dtag, w, fcn,
							 c=""):  # rule_id is arbitrary, as it's not applicable for F/R

					self.profile = profile

					direction = profile.direction

					if direction == "DOWNLINK":
						self.FCN = ""
						self.C = c

					if len(rule_id) != profile.RULE_ID_SIZE:
						print('RULE must be of length RULE_ID_SIZE')
					else:
						self.RULE_ID = rule_id

					if profile.T == "0":
						self.DTAG = ""
					elif len(dtag) != profile.T:
						print('DTAG must be of length T')
					else:
						self.DTAG = dtag

					if len(w) != profile.M:
						print(w)
						print(profile.M)
						print('W must be of length M')
					else:
						self.W = w

					if fcn != "":
						if len(fcn) != profile.N:
							print('FCN must be of length N')
						else:
							self.FCN = fcn

					self.string = "".join([self.RULE_ID, self.DTAG, self.W, self.FCN, self.C])  # self.C ?
					self.bytes = bytes(int(self.string[i:i + 8], 2) for i in range(0, len(self.string), 8))

				def test(self):

					print("HEADER:")
					print(self.string)

					if len(self.string) != self.profile.HEADER_LENGTH:
						print('The header has not been initialized correctly.')
			class Fragment:
				profile = None
				header_length = 0
				rule_id_size = 0
				t = 0
				n = 0
				window_size = 0

				header = None
				payload = None

				def __init__(self, profile, fragment):
					self.profile = profile

					self.header_length = profile.HEADER_LENGTH
					self.rule_id_size = profile.RULE_ID_SIZE
					self.t = profile.T
					self.n = profile.N
					self.m = profile.M

					header = zfill(str(bin(int.from_bytes(fragment[0], 'little')))[2:], self.header_length)
					payload = fragment[1]

					rule_id = str(header[:self.rule_id_size])
					dtag = str(header[self.rule_id_size:self.rule_id_size + self.t])
					window = str(header[self.rule_id_size + self.t:self.rule_id_size + self.t + self.m])
					fcn = str(header[self.rule_id_size + self.t + self.m:self.rule_id_size + self.t + self.m + self.n])
					c = ""
					self.header = Header(self.profile, rule_id, dtag, window, fcn, c)
					self.payload = payload

				def test(self):
					print("Header: " + self.header.string)
					print("Payload: " + str(self.payload))

				def is_all_1(self):
					fcn = self.header.FCN
					fcn_set = set()
					for x in fcn:
						fcn_set.add(x)
					return len(fcn_set) == 1 and "1" in fcn_set

				def is_all_0(self):
					fcn = self.header.FCN
					fcn_set = set()
					for x in fcn:
						fcn_set.add(x)
					return len(fcn_set) == 1 and "0" in fcn_set
			#  -special messages
			class ACK:

				profile = None
				rule_id = None
				dtag = None
				w = None
				bitmap = None
				c = None
				header = ''
				padding = bytes(0)

				def __init__(self, profile, rule_id, dtag, w, bitmap, c):
					self.profile = profile
					# self.header = Header(profile, message.header.RULE_ID, message.header.DTAG.zfill(2), message.header.W[-1],
					# fcn="", c="0")		# [-1]: the least significant bit

					self.rule_id = rule_id
					self.dtag = dtag
					self.w = w
					self.bitmap = bitmap
					self.c = c

					self.header = bytearray((self.rule_id + self.dtag + self.w + self.bitmap + self.c).encode())

					while len(self.header + self.padding) < profile.MTU:
						self.padding += bytes(1)

				def to_string(self):
					return self.header + self.padding

				def to_bytes(self):
					return self.header + self.padding
			# -entities
			class Fragmenter:
				profile = None
				schc_packet = None

				def __init__(self, profile, schc_packet):
					self.profile = profile
					self.schc_packet = schc_packet

				def fragment(self):
					payload_max_length = int((self.profile.MTU - self.profile.HEADER_LENGTH) / 8)
					message = self.schc_packet
					fragment_list = []
					n = self.profile.N
					m = self.profile.M
					number_of_fragments = int(ceil(float(len(message)) / payload_max_length))

					print("[FRGM] Fragmenting message into " + str(number_of_fragments) + " pieces...")

					for i in range(number_of_fragments):
						w = zfill(bin(int(floor((i / (2 ** n - 1) % (2 ** m)))))[2:], 2)
						fcn = zfill(bin((2 ** n - 2) - (i % (2 ** n - 1)))[2:], 3)

						fragment_payload = message[i * payload_max_length:(i + 1) * payload_max_length]

						if len(fragment_payload) < payload_max_length:
							header = Header(self.profile, rule_id="00", dtag="0", w=w, fcn="111", c=0)

						else:
							header = Header(self.profile, rule_id="00", dtag="0", w=w, fcn=fcn, c=0)

						fragment = [header.bytes, fragment_payload]
						# print("[" + header.string + "]" + str(fragment_payload))
						fragment_list.append(fragment)

					print("[FRGM] Fragmentation complete.")

					return fragment_list
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
						if fragment != b'':
							self.schc_fragments.append(Fragment(self.profile, fragment))

					for fragment in self.schc_fragments:
						self.rule_set.add(fragment.header.RULE_ID)
						self.dtag_set.add(fragment.header.DTAG)
						self.window_set.add(fragment.header.W)
						self.fcn_set.add(fragment.header.FCN)

				def reassemble(self):
					fragments = self.schc_fragments
					payload_list = []

					for fragment in fragments:
						payload_list.append(fragment.payload)

					return b"".join(payload_list)
			class Protocol:
				NAME = None
				RULE_ID_SIZE = 0
				L2_WORD_SIZE = 0
				TILE_SIZE = 0
				M = 0
				N = 0
				M = 0
				BITMAP_SIZE = 0
				RCS_SIZE = 0
				RCS_ALGORITHM = None
				T = 0
				MAX_ACK_REQUESTS = 0
				MAX_WIND_FCN = 0
				RETRANSMISSION_TIMER_VALUE = None
				INACTIVITY_TIMER_VALUE = None
				MTU = 0
			class Sigfox(Protocol):
				direction = None
				mode = None

				def __init__(self, direction, mode):

					# print("This protocol is in " + direction + " direction and " + mode + " mode.")

					self.NAME = "SIGFOX"
					self.direction = direction
					self.mode = mode
					self.RETRANSMISSION_TIMER_VALUE = 45  # (45) enough to let a downlink message to be sent if needed
					self.INACTIVITY_TIMER_VALUE = 10  # (60) for demo purposes

					self.N = 0

					self.HEADER_LENGTH = 0

					self.MESSAGE_INTEGRITY_CHECK_SIZE = None  # TBD
					self.RCS_ALGORITHM = None  # TBD

					if direction == "UPLINK":
						self.MTU = 12 * 8

						# if mode == "NO ACK":
						#     self.HEADER_LENGTH = 8
						#     self.RULE_ID_SIZE = 2  # recommended
						#     self.T = 2  # recommended
						#     self.N = 4  # recommended
						#     self.M = 0

						if mode == "ACK ALWAYS":
							pass  # TBD

						if mode == "ACK ON ERROR":
							self.HEADER_LENGTH = 8
							self.RULE_ID_SIZE = 2
							self.T = 1
							self.N = 3
							self.M = 2  # recommended to be single
							self.WINDOW_SIZE = 2 ** self.N - 1
							self.BITMAP_SIZE = 2 ** self.N - 1  # from excel
							self.MAX_ACK_REQUESTS = 3  # SHOULD be 2
							self.MAX_WIND_FCN = 6  # SHOULD be

					if direction == "DOWNLINK":
						self.MTU = 8 * 8
						if mode == "NO ACK":
							self.HEADER_LENGTH = 8
							self.RULE_ID_SIZE = 2
							self.T = 1
							self.M = 2
							self.N = 3
						if mode == "ACK ALWAYS":
							self.HEADER_LENGTH = 8
							self.RULE_ID_SIZE = 2  # recommended
							self.T = 2  # recommended
							self.N = 3  # recommended
							self.M = 1  # MUST be present, recommended to be single
							self.MAX_ACK_REQUESTS = 3  # SHOULD be 2
							self.MAX_WIND_FCN = 6  # SHOULD be

						else:
							pass

			print("Loading functions...")
			#  FUNCTIONS
			def zfill(string, width):
				if len(string) < width:
					return ("0" * (width - len(string))) + string
				else:
					return string
			def insert_index(ls, pos, elmt):
				while len(ls) < pos:
					ls.append([])
				ls.insert(pos, elmt)
			def replace_bit(string, position, value):
				return '%s%s%s' % (string[:position], value, string[position + 1:])
			def find(string, character):
				return [i for i, ltr in enumerate(string) if ltr == character]

			fragment = request_dict["data"]

			# CHECK TIME VALIDATION (INACTIVITY TIMER)
			time_received = request_dict["time"]
			BLOB_NAME = "timestamp"
			BLOB_STR = time_received
			upload_blob(BUCKET_NAME, BLOB_STR, BLOB_NAME)

			profile_uplink = Sigfox("UPLINK", "ACK ON ERROR")
			profile_downlink = Sigfox("DOWNLINK", "NO ACK")
			buffer_size = profile_uplink.MTU
			n = profile_uplink.N
			m = profile_uplink.M
			current_window = 0
			current_window_ack = 0

			if len(fragment) * 8 > buffer_size:
				print("Fragment size is greater than buffer size D:")
				exit(0)

			if not exists_blob(BUCKET_NAME, "all_windows/"):
				create_folder(BUCKET_NAME, "all_windows/")
				for i in range(2 ** m):
					create_folder(BUCKET_NAME, "all_windows/window_%d/" % i)
					for j in range(2 ** n - 1):
						upload_blob(BUCKET_NAME, "", "all_windows/window_%d/fragment_%d_%d" % (i, i, j))
					# create bitmap for each window
					if not exists_blob(BUCKET_NAME, "all_windows/window_%d/bitmap_%d" % (i, i) or size_blob("all_windows/window_%d/bitmap_%d" % (i, i)) == 0):
						bitmap = ""
						for b in range(profile_uplink.BITMAP_SIZE):
							bitmap += "0"
						upload_blob(BUCKET_NAME, bitmap, "all_windows/window_%d/bitmap_%d" % (i, i))

			window = []
			for i in range(2 ** n - 1):
				window.append([b"", b""])

			payload = ''
			fcn_dict = {}
			for j in range(2 ** n - 1):
				fcn_dict[zfill(bin((2 ** n - 2) - (j % (2 ** n - 1)))[2:], 3)] = j

			# A fragment has the format "fragment = [header, payload]".
			data = [bytes([fragment[0]]), bytearray(fragment[1:])]

			# Convert to a Fragment class for easier manipulation.
			fragment_message = Fragment(profile_uplink, data)
			current_window = int(fragment_message.header.W, 2)

			bitmap = read_blob(BLOB_NAME, "all_windows/window_%d/bitmap_%d" % (current_window, current_window))

			try:
				fragment_number = fcn_dict[fragment_message.header.FCN]

				print("[RECV] This corresponds to the " + str(fragment_number) + "th fragment of the " + str(
					current_window) + "th window.")

				bitmap = replace_bit(bitmap, fragment_number, '1')

				upload_blob(BUCKET_NAME, bitmap, "all_windows/window_%d/bitmap_%d" % (current_window, current_window))
				upload_blob(BUCKET_NAME, data[0].decode("utf-8") + data[1].decode("utf-8"), "all_windows/window_%d/fragment_%d_%d" % (current_window, current_window, fragment_number))

			except KeyError:

				print("[RECV] This seems to be the final fragment.")

				bitmap = replace_bit(bitmap, len(bitmap) - 1, '1')
				upload_blob(BUCKET_NAME, bitmap, "all_windows/window_%d/bitmap_%d" % (current_window, current_window))

			rule_id = fragment_message.header.RULE_ID
			dtag = fragment_message.header.DTAG
			w = fragment_message.header.W

			if fragment_message.is_all_0() or fragment_message.is_all_1():
				for i in range(current_window + 1):
					bitmap_ack = read_blob(BUCKET_NAME, "all_windows/window_%d/bitmap%d" (i, i))
					window_ack = i
					if '0' in bitmap_ack:
						break

				if '0' in bitmap_ack and fragment_message.is_all_0():
					number_of_lost_fragments = bitmap_ack.count('0')
					indices = find(bitmap_ack, '0')
					print("[ALLX] Sending ACK for lost fragments...")
					ack = ACK(profile_downlink, rule_id, dtag, zfill(format(window_ack, 'b'), m), bitmap_ack, '0')
					response_json = send_ack(request_dict, ack)
					return response_json, 200

				if fragment_message.is_all_0() and bitmap[0] == '1' and all(bitmap):
					print("[ALLX] Sending ACK after window...")
					ack = ACK(profile_downlink, rule_id, dtag, w, bitmap, '0')
					response_json = send_ack(request_dict, ack)
					return response_json, 200

				if fragment_message.is_all_1():
					last_index = 0
					last_received_index = 0
					i = 0
					j = 0

					while i < 2 ** n - 1:
						if size_blob(BUCKET_NAME, "all_windows/window%d/fragment%d_%d" % (current_window, current_window, i)) == 0:
							last_index = i
							break
						else:
							i += 1

					while j < 2 ** n - 1:
						if exists_blob(BUCKET_NAME, "all_windows/window_%d/fragment%d_%d" % (current_window, current_window, j)) and size_blob(BUCKET_NAME, "all_windows/window_%d/fragment%d_%d" % (current_window, current_window, j)) != 0:
							last_received_index = j + 1
						j += 1

					if last_index != last_received_index:
						number_of_lost_fragments = bitmap_ack.count('0')
						indices = find(bitmap_ack, '0')

						print("[ALLX] Sending NACK for lost fragments...")
						ack = ACK(profile_downlink, rule_id, dtag, zfill(format(window_ack, 'b'), m), bitmap_ack, '0')
						response_json = send_ack(request_dict, ack)
						return response_json, 200

					else:
						fragments = []
						upload_blob(BUCKET_NAME, data[0].decode("utf-8") + data[1].decode("utf-8"), "all_windows/window_%d/fragment_%d_%d" % (current_window, current_window, last_index))

						for i in range(2 ** m):
							for j in range(2 ** n - 1):
								fragment_file = open("./all_windows/window_%d/fragment_%d_%d" % (i, i, j), "r")
								ultimate_header = fragment_file.read(1)
								ultimate_payload = fragment_file.read()
								ultimate_fragment = [ultimate_header.encode(), ultimate_payload.encode()]
								fragments.append(ultimate_fragment)

						print("[ALL1] Last fragment. Reassembling...")
						reassembler = Reassembler(profile_uplink, fragments)
						payload = bytearray(reassembler.reassemble())
						upload_blob(BLOB_NAME, payload.decode("utf-8"), "PAYLOAD")

						print("[ALL1] Reassembled: Sending last ACK")
						bitmap = ''
						for k in range(profile_uplink.BITMAP_SIZE):
							bitmap += '0'
						last_ack = ACK(profile_downlink, rule_id, dtag, w, bitmap, '1')
						response_json = send_ack(request_dict, last_ack)
						return response_json, 200

			return '', 204
		else:
			print('Invalid HTTP Basic Authentication: '
				  '{}'.format(request.authorization))
			return abort(401)
	else:
		print('Invalid HTTP Method to invoke Cloud Function. '
			  'Only POST supported')
		return abort(405)
	# [END functions_callback_data]

