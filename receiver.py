# -*- coding: utf-8 -*-

import socket
import sys

from Entities.Reassembler import Reassembler
from Entities.Sigfox import Sigfox
from Messages.ACK import ACK
from Messages.Fragment import Fragment


def replace_bit(bitmap, index, value):
	return '%s%s%s' % (bitmap[:index], value, bitmap[index + 1:])


print("This is the RECEIVER script for a Sigfox Uplink transmission example")

profile_uplink = Sigfox("UPLINK", "ACK ON ERROR")
profile_downlink = Sigfox("DOWNLINK", "NO ACK")

buffer_size = profile_uplink.MTU
the_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if len(sys.argv) != 2:
	print("python receiver.py [PORT]")

ip = ""
port = int(sys.argv[1])

the_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

the_socket.bind((ip, port))

current_size = 0

n = profile_uplink.N

fragments = []
ack_list = []
bitmap = ''

for i in range(profile_uplink.WINDOW_SIZE):
	bitmap += '1'

i = 0

while True:
	fcn = bin((2 ** n - 2) - (i % (2 ** n - 1)))[2:].zfill(3)

	the_socket.settimeout(profile_uplink.INACTIVITY_TIMER_VALUE)

	fragment, address = the_socket.recvfrom(profile_uplink.MTU)

	if fragment:
		try:
			if fragment.decode() == "":
				break
		except UnicodeDecodeError:
			print("This is not the final fragment.")

		fragment_message = Fragment(profile_uplink, fragment)

		print("FCNs \n Received: " + fragment_message.header.FCN + "\n Expected: " + fcn)

		if fragment_message.is_all_0():
			rule_id = fragment_message.header.RULE_ID
			dtag = fragment_message.header.DTAG
			w = fragment_message.header.W

			fragments.append(fragment)
			current_size += len(fragment)
			print("Received " + str(current_size) + " so far...")
			print("Received All-0: Sending ACK if it exists...")
			if all(char == bitmap[0] for char in bitmap):
				ack = ACK(profile_uplink, rule_id, dtag, w, bitmap, 0)

			# reinitialize bitmap for next window
			bitmap = ''
			for i in range(profile_uplink.WINDOW_SIZE):
				bitmap += '1'

		if fragment_message.is_all_1():

			rule_id = fragment_message.header.RULE_ID
			dtag = fragment_message.header.DTAG
			w = fragment_message.header.W

			fragments.append(fragment)
			current_size += len(fragment)
			print("Received " + str(current_size) + " so far...")

			print("Last fragment. Reassembling...")

			reassembler = Reassembler(profile_uplink, fragments)

			try:
				payload = bytearray(reassembler.reassemble())

				print("Reassembled: Sending last ACK")
				last_ack = ACK(profile_uplink, rule_id, dtag, w, bitmap, 1)
				the_socket.sendto(last_ack.to_string().encode(), address)

			except:
				print("Could not reassemble ):")

			break

		if fragment_message.header.FCN != fcn:
			print("Wrong fragment received. Adding to bitmap...")
			replace_bit(bitmap, i%profile_uplink.WINDOW_SIZE, 0)

		else:
			fragments.append(fragment)
			current_size += len(fragment)
			print("Received " + str(current_size) + " so far...")

	i += 1

the_socket.close()



print(payload)

file = open("received.txt", "wb")
file.write(payload)
file.close()
