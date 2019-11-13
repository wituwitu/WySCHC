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


def replace_bit(string, index, value):
	return '%s%s%s' % (string[:index], value, string[index + 1:])


def find(string, character):
	return [i for i, ltr in enumerate(string) if ltr == character]


def get_index_from_fcn(fcn, n):
	fcn = bin((2 ** n - 2) - (i % (2 ** n - 1)))[2:].zfill(3)


def get_fragments(device_id, auth, limit):
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


for filename in glob.glob("received*"):
	os.remove(filename)

print("This is the RECEIVER script for a Sigfox Uplink transmission example")

profile_uplink = Sigfox("UPLINK", "ACK ON ERROR")
profile_downlink = Sigfox("DOWNLINK", "NO ACK")

buffer_size = profile_uplink.MTU
the_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if len(sys.argv) != 3:
	print("python receiver.py [PORT] [UPLINK LOSS RATE]")

ip = ""
port = int(sys.argv[1])
loss_rate = int(sys.argv[2])

the_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

the_socket.bind((ip, port))

current_size = 0

n = profile_uplink.N

fragments = []
ack_list = []
bitmap = ''

for l in range(profile_uplink.BITMAP_SIZE):
	bitmap += '0'

i = 0
payload = ''

fcn_dict = {}

w = bin(int(floor((i/(2**n - 1) % (2 ** window_size)))))[2:].zfill(2)
fcn = bin((2 ** n - 2) - (i % (2 ** n - 1)))[2:].zfill(3)



while True:
	print("Expecting " + str(i + 1) + "th fragment.")
	fcn = bin((2 ** n - 2) - (i % (2 ** n - 1)))[2:].zfill(3)

	the_socket.settimeout(profile_uplink.INACTIVITY_TIMER_VALUE)

	coin = random.random()

	fragment, address = the_socket.recvfrom(buffer_size)

	if coin * 100 < loss_rate:
		print("The " + str(i + 1) + "th packet was lost.")
		i += 1
		continue

	if fragment:
		data = [bytes([fragment[0]]), bytearray(fragment[1:])]

		try:
			if fragment.decode() == "":
				break
		except UnicodeDecodeError:
			pass

		fragment_message = Fragment(profile_uplink, data)

		print("=FCNs= \n Received: " + fragment_message.header.FCN + "\n Expected: " + fcn)

		if fragment_message.is_all_0():
			rule_id = fragment_message.header.RULE_ID
			dtag = fragment_message.header.DTAG
			w = fragment_message.header.W

			fragments.append(data)
			current_size += len(fragment)
			print("Received " + str(current_size) + " so far...")
			print("Received All-0: Sending ACK if it exists...")

			print(bitmap)

			if '0' in bitmap:
				print("Bitmap: " + bitmap)

				print("Waiting for lost fragments...")

				number_of_lost_fragments = bitmap.count('0')
				indices = find(bitmap, '0')

				for j in range(number_of_lost_fragments):

					index = indices[j]

					print("Sending NACK for " + str(index + 1) + "th fragment...")
					ack = ACK(profile_downlink, rule_id, dtag, w, bitmap, '0')
					the_socket.sendto(ack.to_bytes(), address)

					print("Recovering " + str(index + 1) + "th fragment...")
					fragment, address = the_socket.recvfrom(buffer_size)
					data = [bytes([fragment[0]]), bytearray(fragment[1:])]
					# fragment_message = Fragment(profile_uplink, data)
					fragments[index] = data
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

			fragments.append(data)
			current_size += len(fragment)
			print("Received " + str(current_size) + " so far...")

			print("Last fragment. Reassembling...")

			reassembler = Reassembler(profile_uplink, fragments)

			# try:
			payload = bytearray(reassembler.reassemble())
			print("Reassembled: Sending last ACK")
			last_ack = ACK(profile_downlink, rule_id, dtag, w, bitmap, '1')
			the_socket.sendto(last_ack.to_bytes(), address)

			# except:
			# 	print("Could not reassemble ):")

			break

		elif fragment_message.header.FCN != fcn:
			print("Wrong fragment received. Adding to bitmap...")
			bitmap = replace_bit(bitmap, (profile_uplink.BITMAP_SIZE - 1) - (i % profile_uplink.BITMAP_SIZE), 0)
			print(bitmap)
			print("Generating empty fragment")
			empty = [bytes("0"), bytearray("0")]
			fragments.append(empty)

		else:
			fragments.append(data)
			current_size += len(fragment)
			print("Received " + str(current_size) + " so far...")

	# print(str(i) + "\n")
	i += 1

the_socket.close()

# print(payload)

file = open("received.png", "wb")
file.write(payload)
file.close()
