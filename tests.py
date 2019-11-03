from Entities import SCHC_Frag_Session
from Entities.Reassembler import Reassembler
from Entities.SCHC_Frag_Profile import SCHC_Frag_Profile
from Entities.Sigfox import Sigfox
from Messages.ACK import ACK
from Messages.Fragment import Fragment
from Messages.Header import Header
from Entities.Fragmenter import Fragmenter

# protocol_name = input("PROTOCOL: ")
# direction = input("DIRECTION: ")
# mode = input("MODE: ")
# mtu = input("MTU: ")
# if protocol_name == "SIGFOX":
# 	protocol = Sigfox(direction, mode)

profile = Sigfox("UPLINK", "ACK ON ERROR")
MTU = profile.MTU


data = open("example.txt", "rb")
payload = data.read().decode()
data.close()

print("The payload to be transmitted is: " + payload)

test_header = Header(profile, rule_id="RR", dtag="D", w="WW", fcn="000", c=0)
test_header.test()

fragmenter = Fragmenter(profile, payload)
fragment_list = fragmenter.fragment()

# print("Fragments:")
# for fragment in fragment_list:
# 	print(fragment)

if Fragment(profile, fragment_list[-1]).is_all_1() is True:
	print("All-1 condition satisfied")



# print("Rebuilding message...")
#
# reassembler = Reassembler(profile, fragment_list)
# rebuild = reassembler.reassemble()
#
# print("Rebuilt message: \n" + rebuild)
#
# if payload in rebuild:
# 	print("The message has been rebuilt successfully :D ! Though padding bits are still present.")
# else:
# 	print("There has been an error rebuilding the packet ):")
#
# raw_fragment = fragment_list[0]
# print(raw_fragment)
# fragment = Fragment(profile, raw_fragment)
#
# profile_downlink = Sigfox("DOWNLINK", "NO ACK")
#
# print(profile_downlink.direction)
#
# print("Generating ACK")
# ack_test = ACK(profile_downlink, fragment)
#
# print("All tests complete.")