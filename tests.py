from Entities.SCHC_Frag_Profile import SCHC_Frag_Profile
from Entities.Sigfox import Sigfox
from Messages.Header import Header

# protocol_name = input("PROTOCOL: ")
# direction = input("DIRECTION: ")
# mode = input("MODE: ")
# mtu = input("MTU: ")
# if protocol_name == "SIGFOX":
# 	protocol = Sigfox(direction, mode)

protocol = Sigfox("UPLINK", "NO ACK")


data = list(range(1, 10))
payload = ''.join(map(str, data))

header = Header(protocol)

schc_frag_profile = SCHC_Frag_Profile(protocol, packet)

