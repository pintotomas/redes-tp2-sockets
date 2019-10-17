import queue

class MulticlientHandler:

	def __init__(self):

		self.waiting_queue = queue.Queue()

	def add_socket(self, socket_info):

		self.waiting_queue.put(socket_info)

	def current_socket(self):
		
		return self.waiting_queue.get()

	def empty(self):
		
		return self.waiting_queue.empty()

	def size(self):

		return self.waiting_queue.qsize()