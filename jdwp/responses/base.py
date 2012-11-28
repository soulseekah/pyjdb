import struct

class ResponsePacket( object ):
	"""A Response Packet superclass"""

	def __init__( self ):
		self.length = 11 # Header
		self.id = None
		self.flags = None
		self.error = None
		self.data = None
		
	@staticmethod
	def parse( data ):
		"""Parses the header, data parsing is left up to the child"""
		response = ResponsePacket()
		response.length, response.id, response.flags, \
			response.error = struct.unpack( '>IIBH', data[:11] )
		response.data = data[11:]
		return response
