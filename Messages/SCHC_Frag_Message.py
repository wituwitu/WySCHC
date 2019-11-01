class SCHC_Frag_Message:
	profile = None
	header = None
	payload = None

	def __init__(self, profile, header, payload):
		self.profile = profile
		self.header = header
		self.payload = payload
