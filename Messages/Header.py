class Header:
	profile = None

	RULE_ID = None
	DTAG = None
	W = None
	FCN = None
	RCS = None
	C = None
	COMPRESSED_BITMAP = None

	STRING = None

	def __init__(self, profile, rule_id, dtag, w, fcn, rcs, c, compressed_bitmap):

		length = profile.RULE_ID_SIZE + profile.T + profile.M + profile.N + profile.U + 1 + len(compressed_bitmap)

		if len(rule_id) != profile.RULE_ID_SIZE:
			print('RULE must be of length RULE_ID_SIZE')
		else:
			self.RULE_ID = rule_id

		if profile.T == 0:
			self.DTAG = None
		elif len(dtag) != profile.T:
			print('DTAG must be of length T')
		else:
			self.DTAG = dtag

		if len(w) != profile.M:
			print('W must be of length M')
		else:
			self.W = w

		if len(fcn) != profile.N:
			print('FCN must be of length N')
		else:
			self.FCN = fcn

		if len(rcs) != profile.U:
			print('RCS must be of length U')
		else:
			self.RCS = rcs

		self.C = c

		self.COMPRESSED_BITMAP = compressed_bitmap

		self.STRING = self.RULE_ID + self.DTAG + self.W  + self.FCN + self.RCS + self.C + self.COMPRESSED_BITMAP

		if len(STRING) != length:
			print('The header has not been initialized correctly.')
