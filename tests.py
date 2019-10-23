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
MTU = protocol.MTU


data = list(range(1, 100))
payload = "".join(map(str, data))

print("The payload to be transmitted is: " + payload)

header = Header(protocol, rule_id="XX", dtag="01", w="", fcn="0000", c=0)