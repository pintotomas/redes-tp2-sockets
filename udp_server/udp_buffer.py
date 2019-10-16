class UdpBuffer:

	def __init__(self):

		self.chunks = {}

	def add_chunk(self, chunk_number, chunk):
		"""Agrega un nuevo chunk al buffer"""
		self.chunks[chunk_number] = chunk

	def get_chunk(self, chunk_number):
		"""Obtiene el chunk numero 'chunk_number'"""
		return self.chunks[chunk_number]

	def size(self):
		"""Devuelve la cantidad de chunks en el buffer"""
		return len(self.chunks)