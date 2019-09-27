from Payload import Payload


class Window(Payload):
	WINDOW_SIZE = None
	WINDOW_NUMBER = None
	TILE_LIST = []

	def __init__(self, profile, tile_list, window_number):
		self.WINDOW_SIZE = profile.WINDOW_SIZE
		self.WINDOW_NUMBER = window_number
		self.TILE_LIST = tile_list
		pass