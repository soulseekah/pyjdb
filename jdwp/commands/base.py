import struct

class CommandPacket( object ):
	"""A Command Packet superclass"""

	command = None
	command_set = None
	flags = 0x00

	def __init__( self ):
		self.length = 11 # Header length
		self.id = id( self )
		self.data = ''

	def assemble( self ):
		"""Assembles the header, data assembly is left up to the child"""

		if len( self.data ) + 11 != self.length:
			raise Exception( 'Command header length mismatch, expected %d got %d'
				% ( len( self.data ) + 11, self.length ) )

		return struct.pack( '>IIBBB',
			self.length, self.id, self.flags,
			self.command_set, self.command ) + self.data

