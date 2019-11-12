# -*- coding: utf-8 -*-

import socket
import sys
import os
import time

from Entities.Fragmenter import Fragmenter
from Entities.Sigfox import Sigfox
from Messages.ACK import ACK
from Messages.Fragment import Fragment

print("This is the SENDER script for a Sigfox Uplink transmission example")

profile_uplink = Sigfox("UPLINK", "ACK ON ERROR")
profile_downlink = Sigfox("DOWNLINK", "NO ACK")

the_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if len(sys.argv) != 4:
	print("python sender.py [IP] [PORT] [FILENAME]")
	sys.exit()

ip = sys.argv[1]
port = int(sys.argv[2])
filename = sys.argv[3]

address = (ip, port)

# data = open(filename, "rb")
# payload = data.read().decode()
# data.close()

with open(filename, "rb") as data:
	f = data.read()
	payload = bytearray(f)

print(f)

print(payload)
total_size = len(payload)
current_size = 0
percent = round(0, 2)

fragmenter = Fragmenter(profile_uplink, payload)
fragment_list = fragmenter.fragment()

ack = None
last_ack = None
i = 0

while i < len(fragment_list):
	# try:
	#     data = fragment_list[i]
	# except IndexError:
	#     print("Sending empty message")
	#     the_socket.sendto("".encode(), address)
	#     break

	data = bytes(fragment_list[i][0] + fragment_list[i][1])


	print(profile_uplink.MTU)
	print(len(data)*8)
	print(len(bytes(fragment_list[i][0])))
	print(len(bytes(fragment_list[i][1])))

	the_socket.sendto(data, address)

	current_size += len(data)
	percent = round(float(current_size) / float(total_size) * 100, 2)

	print("Sending...")
	print(str(current_size) + " / " + str(total_size) + ", " + str(percent) + "%")

	print("converting to fragment")

	fragment = Fragment(profile_uplink, fragment_list[i])

	if fragment.is_all_0():
		the_socket.settimeout(1)  # profile_uplink.RETRANSMISSION_TIMER_VALUE
		try:
			ack, address = the_socket.recvfrom(profile_downlink.MTU)
			index = profile_uplink.RULE_ID_SIZE + profile_uplink.T + profile_uplink.WINDOW_SIZE
			bitmap = ack.decode()[index:index + profile_uplink.WINDOW_SIZE]

			unsent_fragments = []

			for j in range(len(bitmap)):
				if bitmap[j] == '0':
					data = bytearray(fragment_list[i-j][0].encode()) + fragment_list[i-j][1]
					print(data)
					the_socket.sendto(data, address)

		except:
			print("No ACK received.")

	# En este caso, se tiene la opción de enviar al final un SCHC ACK REQ para verificar que los
	# fragmentos retransmitidos han sido recibidos correctamente, o no. Esto es algo que aún no me queda
	# claro si sea estrictamente necesario o si podemos simplemente continuar con la transmisión de los
	# siguientes fragmentos… Tiendo a esta última opción.

	if fragment.is_all_1():
		print("Waiting for last ACK...")
		requests = 1
		while requests <= profile_uplink.MAX_ACK_REQUESTS:
			the_socket.settimeout(profile_uplink.RETRANSMISSION_TIMER_VALUE)
			try:
				last_ack, address = the_socket.recvfrom(profile_downlink.MTU)
				index = profile_uplink.RULE_ID_SIZE + profile_uplink.T + 2*profile_uplink.WINDOW_SIZE
				c = last_ack.decode()[index]
				print("Last ACK received with C = " + c + ". End of transmission.")
				the_socket.sendto("".encode(), address)
				break
			except:
				requests += 1
				print("Trying for " + str(requests) + "th time")
			if requests > profile_uplink.MAX_ACK_REQUESTS:
				print("MAX_ACK_REQUESTS reached. Wat do?")

	# for ack in ack_list:  # para cada ACK recibido
	# 	fcn = ACK(profile_downlink, ack).header.FCN
	# 	# obtengo su FCN # OJO AQUI: ACK crea un ACK para el ACK, no lo reinstaura.
	# 	# Pero los headers son iwales así que igual apaña
	# 	for fragment in fragment_list:
	# 		if fcn == Fragment(profile_uplink, fragment).header.FCN:
	# 			the_socket.sendto(fragment.encode(), address)
	# 			# reenvío todos los fragmentos cuyos FCN aparezcan en ACKs
	# 		else:
	# 			print("Received ACK but no corresponding fragment found D:")

	if last_ack:
		break
	else:
		i += 1

the_socket.close()

time.sleep(1)

import filecmp

print(filecmp.cmp("received.png", filename))
