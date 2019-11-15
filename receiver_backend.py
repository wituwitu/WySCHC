# -*- coding: utf-8 -*-
import random
import socket
import sys
import os
import glob
import requests
import json

from Entities.Reassembler import Reassembler
from Entities.Sigfox import Sigfox
from Messages.ACK import ACK
from Messages.Fragment import Fragment


def replace_bit(string, position, value):
	return '%s%s%s' % (string[:position], value, string[position + 1:])


def find(string, character):
	return [i for i, ltr in enumerate(string) if ltr == character]


def get_fragments(device_id, limit,
				  auth="Basic NWRjNDY1ZjRlODMzZDk0MWY2Y2M0Y2QzOjBmMjQ1NDI0MTg2YTMxNDhjYzJkNWJiYjI0MDUwOWY5"):
	url = "https://api.sigfox.com/v2/devices/{}/messages".format(device_id)
	payload = ''
	headers = {
		"Accept": "application/json",
		"Content-Type": "application/x-www-form-urlencoded",
		"Authorization": auth,
		"cache-control": "no-cache"
	}
	params = {"limit": limit}
	response = requests.request("GET", url, data=payload, headers=headers, params=params)
	parsed = response.json()
	byte_array = []
	values = parsed["data"]
	for val in values:
		byte_array.append(bytearray.fromhex(val["data"]))
	byte_array.reverse()
	return byte_array


# Delete the previously received file (only on offline testing)
for filename in glob.glob("received*"):
	os.remove(filename)

print("This is the RECEIVER script for a Sigfox Uplink transmission example")

if len(sys.argv) != 3:
	print("python receiver.py [DEVICE ID] [LIMIT]")
	sys.exit()

device_id = sys.argv[1]
limit = sys.argv[2]

# Initialize variables.
profile_uplink = Sigfox("UPLINK", "ACK ON ERROR")
profile_downlink = Sigfox("DOWNLINK", "NO ACK")
buffer_size = profile_uplink.MTU
n = profile_uplink.N
w = profile_uplink.WINDOW_SIZE
# the_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# the_socket.bind((ip, port))
current_window = 0
fragments = []
window = []
payload = ''
bitmap = ''
for l in range(profile_uplink.BITMAP_SIZE):
	bitmap += '0'
fcn_dict = {}
for j in range(2 ** n - 1):
	fcn_dict[bin((2 ** n - 2) - (j % (2 ** n - 1)))[2:].zfill(3)] = j

# Get fragments from backend

backend_fragments = get_fragments(device_id, limit)
print(backend_fragments)

for i in range(len(backend_fragments)):

	# Initialize window
	for j in range(2 ** n - 1):
		window.append(b"")

	fragment = backend_fragments[i]
	data = [bytes([fragment[0]]), bytearray(fragment[1:])]
	fragment_message = Fragment(profile_uplink, data)

	try:
		fragment_number = fcn_dict[fragment_message.header.FCN]
		print("[RECV] This corresponds to the " + str(fragment_number) + "th fragment of the " + str(
			current_window) + "th window.")

		# Set the fragment_number-th bit of the bitmap to 1 and add the fragment to the fragment_number-th position
		# in the current window.
		bitmap = replace_bit(bitmap, fragment_number, '1')
		window[fragment_number] = data

	# If the FCN does not have a corresponding fragment number, then it almost certainly is an All-1
	except KeyError:

		# Set the rightmost bit of the bitmap to 1 (See SCHC draft).
		print("[RECV] This seems to be the final fragment.")
		bitmap = replace_bit(bitmap, len(bitmap) - 1, '1')

		# Extract information from the fragment class.
		rule_id = fragment_message.header.RULE_ID
		dtag = fragment_message.header.DTAG
		w = fragment_message.header.W

		# If the fragment is at the end of a window (All-0 or All-1).
		if fragment_message.is_all_0() or fragment_message.is_all_1():

			# Add all fragments from the window to the "fragments" array
			for m in range(2 ** n - 1):
				fragments.append(window[m])

			# If the last received fragment is an All-0, reinitialize variables for next loop
			if fragment_message.is_all_0():
				current_window += 1
				window = []
				bitmap = ''
				for k in range(profile_uplink.BITMAP_SIZE):
					bitmap += '0'

			# If the last received fragment is an All-1, start reassembling.
			if fragment_message.is_all_1():

				# If everything has gone according to plan, there shouldn't be any empty spaces
				# between two received fragments. So the first occurrence of an empty space should be the position
				# of the final fragment.
				last_index = fragments.index(b'')
				fragments[last_index] = data

				# Reassemble.
				print("[ALL1] Last fragment. Reassembling...")
				reassembler = Reassembler(profile_uplink, fragments)
				payload = bytearray(reassembler.reassemble())

				# Send the last ACK with the C bit set to 1.
				print("[ALL1] Reassembled: Sending last ACK")

				# End loop
				break


# Close the socket and write the received file.
file = open("received.txt", "wb")
file.write(payload)
file.close()
