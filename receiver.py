import socket
import sys

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
percent = round(0, 2)
can_receive = True

fcn = "".zfill(profile_uplink.N)

the_socket.settimeout(0.5)  # No sé qué poner acá

downloading_file = open("received.txt", "wb")

while True:
    fragment, address = the_socket.recvfrom(profile_uplink.MTU)

    if fragment:
        fragment_message = Fragment(profile_uplink, fragment.decode())
        if fragment_message.header.FCN != fcn:
            ack = ACK(profile_downlink, fragment)
            the_socket.sendto(ack.to_string().encode(), address)
