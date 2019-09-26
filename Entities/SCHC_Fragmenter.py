from Entities import SCHC_Frag_Session
class SCHC_Fragmenter:
	NO_ACK_MODE = 1
	ACK_ALWAYS_MODE = 2
	ACK_ON_ERROR_MODE = 3

	profile = None
	send_function = None
	get_dr_function = None

	def __init__(self, profile, send_function, get_dr_function):
		self.profile = profile
		self.send_function = send_function
		self.get_dr_function = get_dr_function


