import struct
import time

class CommandPacket( object ):
	"""A Command Packet superclass"""

	command = None
	command_set = None
	flags = 0x00

	def __init__( self ):
		self.length = 11 # Header length
		# When using id() the address can be garbage collected and reused within seconds
		# so we use an additional time offset and wrap everything up to 32-bits
		# in theory this should provide some space between shared object addresses
		self.id = int( ( id( self ) + ( time.time() * 1000000 ) ) % 0xffffffff )
		self.data = ''

	def assemble( self ):
		"""Assembles the header, data assembly is left up to the child"""

		if len( self.data ) + 11 != self.length:
			raise Exception( 'Command header length mismatch, expected %d got %d'
				% ( len( self.data ) + 11, self.length ) )

		return struct.pack( '>IIBBB',
			self.length, self.id, self.flags,
			self.command_set, self.command ) + self.data
