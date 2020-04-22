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
from functions import *


def insert_index(list, pos, elmt):
	while len(list) < pos:
		list.append([])
	list.insert(pos, elmt)


def replace_bit(string, position, value):
	return '%s%s%s' % (string[:position], value, string[position + 1:])


def find(string, character):
	return [i for i, ltr in enumerate(string) if ltr == character]


# def get_fragments(device_id, limit,
# 				  auth="Basic NWRjNDY1ZjRlODMzZDk0MWY2Y2M0Y2QzOjBmMjQ1NDI0MTg2YTMxNDhjYzJkNWJiYjI0MDUwOWY5"):
# 	url = "https://api.sigfox.com/v2/devices/{}/messages".format(device_id)
# 	payload = ''
# 	headers = {
# 		"Accept": "application/json",
# 		"Content-Type": "application/x-www-form-urlencoded",
# 		"Authorization": auth,
# 		"cache-control": "no-cache"
# 	}
# 	params = {"limit": limit}
# 	response = requests.request("GET", url, data=payload, headers=headers, params=params)
# 	parsed = response.json()
# 	byte_array = []
# 	values = parsed["data"]
# 	for val in values:
# 		byte_array.append(bytearray.fromhex(val["data"]))


# Delete the previously received file (only on offline testing)
for filename in glob.glob("received*"):
	os.remove(filename)

print("This is the RECEIVER script for a Sigfox Uplink transmission example")

if len(sys.argv) != 3:
	print("python receiver.py [PORT] [UPLINK LOSS RATE]")
	sys.exit()

ip = ""
port = int(sys.argv[1])
loss_rate = int(sys.argv[2])

# Initialize variables.
the_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
the_socket.bind((ip, port))

profile_uplink = Sigfox("UPLINK", "ACK ON ERROR")
profile_downlink = Sigfox("DOWNLINK", "NO ACK")
buffer_size = profile_uplink.MTU
n = profile_uplink.N
m = profile_uplink.M

current_window = 0
fragments = []

window = []
for i in range(2 ** n - 1):
	window.append([b"", b""])

all_windows = []
for i in range(2**m):
	all_windows.append([])
	for j in range(2 ** n - 1):
		all_windows[i].append([b"", b""])


payload = ''
bitmap = ''
for l in range(profile_uplink.BITMAP_SIZE):
	bitmap += '0'
fcn_dict = {}
for j in range(2 ** n - 1):
	fcn_dict[zfill(bin((2 ** n - 2) - (j % (2 ** n - 1)))[2:], 3)] = j

# Start receiving fragments.
while True:


	# Receive fragment
	try:
		print(bitmap)
		fragment, address = the_socket.recvfrom(buffer_size)

		# A fragment has the format "fragment = [header, payload]".
		data = [bytes([fragment[0]]), bytearray(fragment[1:])]

		# Convert to a Fragment class for easier manipulation.
		fragment_message = Fragment(profile_uplink, data)

		# This avoids All-0 and All-1 fragments being lost for testing purposes.
		# TODO: What happens when All-0 or All-1 get lost?
		if not fragment_message.is_all_0() and not fragment_message.is_all_1():

			# Lose packet with certain probability and go to the start of the loop.
			coin = random.random()
			if coin * 100 < loss_rate:
				print("[LOSS] The packet was lost.")
				continue

		# Try finding the fragment number from the FCN of the fragment.
		try:
			fragment_number = fcn_dict[fragment_message.header.FCN]
			current_window = int(fragment_message.header.W, 2)

			print("[RECV] This corresponds to the " + str(fragment_number) + "th fragment of the " + str(
				current_window) + "th window.")

			bitmap = replace_bit(bitmap, fragment_number, '1')
			all_windows[current_window][fragment_number] = data

		# If the FCN does not have a corresponding fragment number, then it almost certainly is an All-1
		except KeyError:

			# In the Bitmap for the last window, the bit at the right-most position	corresponds either to the tile
			# numbered 0 or to a tile that is sent / received as "the last one of the SCHC Packet" without explicitly
			# stating it snumber.

			# Set the rightmost bit of the bitmap to 1 (See SCHC draft).
			print("[RECV] This seems to be the final fragment.")
			bitmap = replace_bit(bitmap, len(bitmap) - 1, '1')

		# Extract information from the fragment class.
		rule_id = fragment_message.header.RULE_ID
		dtag = fragment_message.header.DTAG
		w = fragment_message.header.W

		# If the fragment is at the end of a window (All-0 or All-1).
		if fragment_message.is_all_0() or fragment_message.is_all_1():
			ack_has_been_sent = False

			print(bitmap)

			# Check for lost fragments in the bitmap.
			if '0' in bitmap:

				number_of_lost_fragments = bitmap.count('0')
				indices = find(bitmap, '0')
				print(indices)

				# Create an ACK object and send it as bytes to the sender.
				print("[ALLX] Sending NACK for lost fragments...")
				ack = ACK(profile_downlink, rule_id, dtag, w, bitmap, '0')
				print(ack.to_string())
				the_socket.sendto(ack.to_bytes(), address)
				ack_has_been_sent = True

				# For every lost fragment:
				for j in range(number_of_lost_fragments):
					index = indices[j]

					# Try recovering the index-th fragment
					try:
						print("[ALLX] Recovering " + str(index) + "th fragment...")
						fragment_recovered, address = the_socket.recvfrom(buffer_size)
						data_recovered = [bytes([fragment_recovered[0]]), bytearray(fragment_recovered[1:])]
						fragment_message_recovered = Fragment(profile_uplink, data_recovered)
						fragment_number_recovered = fcn_dict[fragment_message_recovered.header.FCN]
						current_window_recovered = int(fragment_message_recovered.header.W, 2)
						print("[ALLX] This corresponds to the " + str(
							fragment_number_recovered) + "th fragment of the " + str(
							current_window_recovered) + "th window.")
						all_windows[current_window_recovered][index] = data_recovered
						print("[ALLX] Recovered")
						bitmap = replace_bit(bitmap, fragment_number_recovered, '1')

					# TODO: What happens when the resent fragment gets lost?

					# If the index-th fragment's FCN does not have a fragment number, then it is invalid
					except KeyError:
						print("No fragment to be recovered")
						continue

					# If no fragment was received, something nasty happened.
					except socket.timeout:
						print("Timed out")
						exit(1)

				if '0' in bitmap and not fragment_message.is_all_1():
					print("A resent fragment has been lost. What should I do?")
					exit(1)

			# If the last received fragment is an All-0 and every fragment has been received,
			# send empty ACK and reinitialize variables for next loop

			if fragment_message.is_all_0() and bitmap[0] == '1' and all(bitmap):
				if not ack_has_been_sent:
					print("[ALLX] Sending NACK after window...")
					ack = ACK(profile_downlink, rule_id, dtag, w, bitmap, '0')
					the_socket.sendto(ack.to_bytes(), address)
				bitmap = ''
				for k in range(profile_uplink.BITMAP_SIZE):
					bitmap += '0'

			# If the last received fragment is an All-1, start reassembling.
			if fragment_message.is_all_1():

				# If everything has gone according to plan, there shouldn't be any empty spaces
				# between two received fragments. So the first occurrence of an empty space should be the position
				# of the final fragment.
				last_index = all_windows[current_window].index([b'', b''])
				all_windows[current_window][last_index] = data

				for i in range(2 ** m):
					for j in range(2 ** n - 1):
						fragments.append(all_windows[i][j])

				# Reassemble.
				print("[ALL1] Last fragment. Reassembling...")
				reassembler = Reassembler(profile_uplink, fragments)
				payload = bytearray(reassembler.reassemble())

				# Send the last ACK with the C bit set to 1.
				print("[ALL1] Reassembled: Sending last ACK")

				# "if the C bit is set to 1, no bitmap is carried."
				bitmap = ''
				for k in range(profile_uplink.BITMAP_SIZE):
					bitmap += '0'

				last_ack = ACK(profile_downlink, rule_id, dtag, w, bitmap, '1')
				the_socket.sendto(last_ack.to_bytes(), address)

				# End loop
				break

	# If no fragment was received, something nasty happened.
	except socket.timeout:
		print("Timed out")
		exit(1)

	print("To the next...")

# Close the socket and write the received file.
the_socket.close()

# Change the extension of the file if you need, default is .txt
file = open("received.txt", "wb")
file.write(payload)
file.close()
