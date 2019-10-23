from Entities import SCHC_Frag_Session
from Entities.SCHC_Frag_Profile import SCHC_Frag_Profile
from Entities.Sigfox import Sigfox
from Messages.Header import Header
from Entities.Fragmenter import Fragmenter

# protocol_name = input("PROTOCOL: ")
# direction = input("DIRECTION: ")
# mode = input("MODE: ")
# mtu = input("MTU: ")
# if protocol_name == "SIGFOX":
# 	protocol = Sigfox(direction, mode)

protocol = Sigfox("UPLINK", "ACK ON ERROR")
MTU = protocol.MTU


data = list(range(1, 100))
payload = "".join(map(str, data))

print("The payload to be transmitted is: " + payload)

test_header = Header(protocol, rule_id="RR", dtag="D", w="WW", fcn="000", c=0)
test_header.test()

fragmenter = Fragmenter(protocol, payload)
fragment_list = fragmenter.fragment()

print("Fragments:")
for fragment in fragment_list:
	print(fragment)
