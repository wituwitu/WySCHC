from network import Sigfox
import socket
import binascii

# init Sigfox for RCZ4 (Chile)
sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ4)
s = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)


# s.setblocking(True)
s.setblocking(True)

# configure it as uplink only
s.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, False)

s.settimeout(10)
# send some bytes

s.send("Hola m8")
print("Done")
