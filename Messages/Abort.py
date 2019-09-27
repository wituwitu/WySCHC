from Messages import SCHC_Frag_Message


class Abort(SCHC_Frag_Message):
	RECEIVER_ABORT = 1
	SENDER_ABORT = 0

	def __init__(self):
		pass
