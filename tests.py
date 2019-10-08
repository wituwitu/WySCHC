from Entities.Protocol import Protocol
from Entities.Sigfox import Sigfox

protocol_name = input("PROTOCOL: ")
direction = input("DIRECTION: ")
mode = input("MODE: ")

if protocol_name == "SIGFOX":
	protocol = Sigfox(direction, mode)