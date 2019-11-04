# -*- coding: utf-8 -*-

import socket
import sys

from Entities.Reassembler import Reassembler
from Entities.Sigfox import Sigfox
from Messages.ACK import ACK
from Messages.Fragment import Fragment


def replace_bit(string, index, value):
	return '%s%s%s' % (string[:index], value, string[index + 1:])


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

for l in range(profile_uplink.BITMAP_SIZE):
	bitmap += '1'

i = 0
payload = ''

while True:
	print(i)
	fcn = bin((2 ** n - 2) - (i % (2 ** n - 1)))[2:].zfill(3)

	the_socket.settimeout(profile_uplink.INACTIVITY_TIMER_VALUE)

	fragment, address = the_socket.recvfrom(buffer_size)

	if fragment:
		try:
			if fragment.decode() == "":
				break
		except UnicodeDecodeError:
			pass

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

			print(bitmap)

			if '0' in bitmap:
				print("Bitmap: " + bitmap)
				ack = ACK(profile_uplink, rule_id, dtag, w, bitmap, 0)

				print("Waiting for lost fragments...")

				number_of_lost_fragments = bitmap.count('0')

				for j in range(number_of_lost_fragments):
					fragment, address = the_socket.recvfrom(buffer_size)
					fragment_message = Fragment(profile_uplink, fragment)
					fragments.append(fragment)
					current_size += len(fragment)
					print("Received " + str(current_size) + " so far...")

			# reinitialize bitmap for next window
			bitmap = ''
			for k in range(profile_uplink.BITMAP_SIZE):
				bitmap += '1'

		elif fragment_message.is_all_1():

			rule_id = fragment_message.header.RULE_ID
			dtag = fragment_message.header.DTAG
			w = fragment_message.header.W

			fragments.append(fragment)
			current_size += len(fragment)
			print("Received " + str(current_size) + " so far...")

			print("Last fragment. Reassembling...")

			reassembler = Reassembler(profile_uplink, fragments)

			# try:
			payload = bytearray(reassembler.reassemble())
			print("Reassembled: Sending last ACK")
			last_ack = ACK(profile_uplink, rule_id, dtag, w, bitmap, '1')
			the_socket.sendto(last_ack.to_string().encode(), address)

			# except:
			# 	print("Could not reassemble ):")

			break

		elif fragment_message.header.FCN != fcn:
			print("Wrong fragment received. Adding to bitmap...")
			replace_bit(bitmap, profile_uplink.WINDOW_SIZE - (i % profile_uplink.BITMAP_SIZE), 0)
			print(bitmap)

		else:
			fragments.append(fragment)
			current_size += len(fragment)
			print("Received " + str(current_size) + " so far...")

	print(str(i) + "\n")
	i += 1

the_socket.close()

# print(payload)

file = open("received.png", "wb")
file.write(payload)
file.close()
