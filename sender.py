# -*- coding: utf-8 -*-
import getopt
import socket
import sys
import time
import filecmp

from Entities.Fragmenter import Fragmenter
from Entities.Sigfox import Sigfox
from Messages.Fragment import Fragment

print("This is the SENDER script for a Sigfox Uplink transmission example")

if len(sys.argv) < 4:
	print("python sender.py [IP] [PORT] [FILENAME] [-hv]")
	sys.exit()

verbose = False

try:
	opts, args = getopt.getopt(sys.argv[4:], "hv")
	for opt, arg in opts:
		if opt == '-h':
			print("python sender.py [IP] [PORT] [FILENAME] [-hv]")
			sys.exit()
		elif opt == '-v':
			verbose = True
		else:
			print("Unhandled")
except getopt.GetoptError as err:
	print(str(err))

ip = sys.argv[1]
port = int(sys.argv[2])
filename = sys.argv[3]
address = (ip, port)

# Read the file to be sent.
with open(filename, "rb") as data:
	f = data.read()
	payload = bytearray(f)

# Initialize variables.
total_size = len(payload)
current_size = 0
percent = round(0, 2)
ack = None
last_ack = None
i = 0
current_window = 0
profile_uplink = Sigfox("UPLINK", "ACK ON ERROR")
profile_downlink = Sigfox("DOWNLINK", "NO ACK")
the_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Fragment the file.
fragmenter = Fragmenter(profile_uplink, payload)
fragment_list = fragmenter.fragment()

# Start sending fragments.
while i < len(fragment_list):

	# A fragment has the format "fragment = [header, payload]".
	data = bytes(fragment_list[i][0] + fragment_list[i][1])

	if verbose:
		print(str(i) + "th fragment:")
		print(data)

	current_size += len(fragment_list[i][1])
	percent = round(float(current_size) / float(total_size) * 100, 2)

	# Send the data.
	print("Sending...")
	the_socket.sendto(data, address)
	print(str(current_size) + " / " + str(total_size) + ", " + str(percent) + "%")

	# Convert to a Fragment class for easier manipulation.
	fragment = Fragment(profile_uplink, fragment_list[i])

	# If a fragment is an All-0 or an All-1:
	if fragment.is_all_0() or fragment.is_all_1():

		# Set the timeout for RETRANSMISSION_TIMER_VALUE.
		the_socket.settimeout(profile_uplink.RETRANSMISSION_TIMER_VALUE)

		# Try receiving an ACK from the receiver.
		try:
			ack, address = the_socket.recvfrom(profile_downlink.MTU)
			print("ACK received.")
			index = profile_uplink.RULE_ID_SIZE + profile_uplink.T + profile_uplink.WINDOW_SIZE
			bitmap = ack.decode()[index:index + profile_uplink.BITMAP_SIZE]
			index_c = index + profile_uplink.BITMAP_SIZE
			c = ack.decode()[index_c]

			# If the C bit of the ACK is set to 1 and the fragment is an All-1 then we're done.
			if c == '1' and fragment.is_all_1():
				# TODO: Check if the W field is correct (see SCHC draft)
				print("Last ACK received: Fragments reassembled successfully. End of transmission.")
				break

			# If the C bit is set to 1 and the fragment is an All-0 then something naughty happened.
			elif c == '1' and fragment.is_all_0():
				print("You shouldn't be here. (All-0 with C = 1)")
				exit(1)

			# If the C bit has not been set:
			elif c == '0':

				# Check the bitmap.
				for j in range(len(bitmap)):

					# If the j-th bit of the bitmap is 0, then the j-th fragment was lost.
					if bitmap[j] == '0':
						print("The " + str(j) + "th (" + str(
							(2 ** profile_uplink.N - 1) * current_window + j) + " / " + str(
							len(fragment_list)) + ") fragment was lost! Sending again...")

						# Try sending again the lost fragment.
						try:
							fragment_to_be_resent = fragment_list[(2 ** profile_uplink.N - 1) * current_window + j]
							data_to_be_resent = bytes(fragment_to_be_resent[0] + fragment_to_be_resent[1])
							print(data_to_be_resent)
							the_socket.sendto(data_to_be_resent, address)
						# TODO: What happens when the resent fragment gets lost?

						# If the fragment wasn't found, it means we're at the last window with no fragment
						# to be resent. The last fragment received is an All-1.
						except IndexError:
							print("No fragment found.")

							# Request last ACK sending the All-1 again.
							the_socket.sendto(data, address)

				# After sending the lost fragments, if the last received fragment was an All-1 we need to receive
				# the last ACK.
				if fragment.is_all_1():

					# Set the timeout for RETRANSMISSION_TIMER_VALUE
					the_socket.settimeout(profile_uplink.RETRANSMISSION_TIMER_VALUE)

					# Try receiving the last ACK.
					try:
						last_ack, address = the_socket.recvfrom(profile_downlink.MTU)
						c = last_ack.decode()[index_c]

						# If the C bit is set to 1 then we're done.
						if c == '1':
							print("Last ACK received: Fragments reassembled successfully. End of transmission.")
							break

						# If the C bit is 0 then something naughty happened.
						else:
							print("You shouldn't be here. (Last ACK with C = 0)")
							exit(0)

					# If the last ACK was not received, raise an error.
					except socket.timeout:
						# TODO: Add requests up to MAX_ACK_REQUESTS
						print("Last ACK has not been received.")
						exit(1)

			# Proceed to next window.
			print("Proceeding to next window")
			current_window += 1

		# If no ACK was received, it's safe to assume that no fragments went lost... Or did they?
		except socket.timeout:
			# TODO: What happens when the ACK gets lost?
			print("No ACK received. We'll assume that no fragments were lost :D")

			# Proceed to next window.
			print("Proceeding to next window")
			current_window += 1

	# Continue to next fragment
	i += 1

# Close the socket and wait for the file to be reassembled
the_socket.close()
time.sleep(1)

# Compare if the reassembled file is the same as the original (only on offline testing)
print(filecmp.cmp("received.png", filename))
