# Glossary
# T: DTag size
# N: Fragment Compressed Number (FCN) size
# M: Window identifier (present only if windows are used) size
# U: Reassembly Check Sequence (RCS) size


class Header:
	profile = None

	RULE_ID = None
	DTAG = None
	W = None
	FCN = None
	RCS = None
	C = None
	COMPRESSED_BITMAP = None

	STRING = ""

	def __init__(self, profile, rule_id, dtag, w, fcn, c): 	# rule_id is arbitrary, as it's not applicable for F/R

		length = profile.RULE_ID_SIZE + profile.T + profile.M + profile.N + profile.WINDOW_SIZE 	# + 1 ?		# The 1 is the size of C

		print("This header is of length " + str(length) + " bits.")

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

		self.C = c

		self.STRING = "".join(map(str, [self.RULE_ID, self.DTAG, self.W, self.FCN])) # self.C ?

		print(self.STRING)

		if len(self.STRING) != length:
			print('The header has not been initialized correctly.')
