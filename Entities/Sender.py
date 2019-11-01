import socket
import sys
import os

from Entities.Fragmenter import Fragmenter
from Entities.Sigfox import Sigfox

print("This is the SENDER script for a Sigfox Uplink transmission example")

profile = Sigfox("UPLINK", "ACK ON ERROR")
buffer_size = profile.MTU
the_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if len(sys.argv) != 2:
    print("python sender.py [IP] [PORT] [FILENAME]")
    sys.exit()

ip = sys.argv[1]
port = sys.argv[2]
filename = sys.argv[3]
total_size = os.path.getsize(filename)
current_size = 0
percent = round(0, 2)
address = (ip, port)

payload = open(filename, "rb")

fragmenter = Fragmenter(profile, payload)
fragment_list = fragmenter.fragment()

for fragment in fragment_list:
    the_socket.sendto(fragment, address)
    the_socket.settimeout(0.5)
    try_counter = 0

    while True:



