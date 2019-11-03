# -*- coding: utf-8 -*-

import socket
import sys

from Entities.Reassembler import Reassembler
from Entities.Sigfox import Sigfox
from Messages.ACK import ACK
from Messages.Fragment import Fragment

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

i = 0

while True:
	fcn = bin((2 ** n - 2) - (i % (2 ** n - 1)))[2:].zfill(3)

	the_socket.settimeout(profile_uplink.INACTIVITY_TIMER_VALUE)

	fragment, address = the_socket.recvfrom(profile_uplink.MTU)

	if fragment:
		if fragment.decode() == "":
			break
		fragment_message = Fragment(profile_uplink, fragment.decode())

		print("FCNs \n Received: " + fragment_message.header.FCN + "\n Expected: " + fcn)

		if fragment_message.header.FCN != fcn:
			print("Wrong fragment received. Generating ACK...")
			ack = ACK(profile_downlink, fragment_message)
			ack_list.append(ack)
		else:
			fragments.append(fragment)
			current_size += len(fragment)
			print("Received " + str(current_size) + " so far...")

			if fragment_message.is_all_0():
				print("Received All-0: Sending ACKs if they exist...")
				for ack in ack_list:
					the_socket.sendto(ack.to_string().encode(), address)

			if fragment_message.is_all_1():
				print("Received All-1: Sending last ACK")
				last_ack = ACK(profile_downlink, fragment)
				the_socket.sendto(last_ack.to_string().encode(), address)

the_socket.close()

reassembler = Reassembler(profile_uplink, fragments)
payload = reassembler.reassemble()

file = open("received.txt", "wb")
file.write(payload)
file.close()
