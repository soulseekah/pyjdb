import argparse
import socket
import struct
import StringIO 
	
class CommandPacket():
	"""A Command Packet superclass"""

	def __init__( self ):
		self.length = 11 # Header
		self.id = 0
		self.flags = 0x00
		self.command_set = 0
		self.command = 0
		self.data = ''

	@staticmethod
	def parse( data ):
		pass
	def assemble( self ):
		return struct.pack( '>IIBBBp',
			self.length, self.id, self.flags, self.command_set, self.command, self.data )

class ResponsePacket():
	"""A Response Packet superclass"""

	def __init__( self ):
		self.length = 11 # Header
		self.id = None
		self.flags = None
		self.error = None
		self.data = None
		
	@staticmethod
	def parse( data ):
		response = ResponsePacket()
		response.length, response.id, response.flags, \
			response.error = struct.unpack( '>IIBH', data[:11] )
		response.data = data[11:]
		return response
	def assemble():
		pass

def attach( address ):
	"""Attach to a running VM"""

	address = address.split( ':' )
	address = socket.getaddrinfo( address[0], address[1], socket.AF_INET, 0, socket.SOL_TCP )
	address = address.pop()[4] if len( address ) else None

	s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	s.connect( address )

	# Let's shake hands
	s.send( 'JDWP-Handshake' )
	handshake = s.recv( 16 )

	if handshake != 'JDWP-Handshake':
		raise Exception( 'Unexpected JDWP handshake response: %s' % handshake )

	# Get JVM version
	command = CommandPacket()
	command.command = 1 # Version
	command.command_set = 1 # VirtualMachine
	s.send( command.assemble() )

	response = ResponsePacket.parse( s.recv( 128 )	)
	data = StringIO.StringIO( response.data )
	description = data.read( struct.unpack( '>I', data.read( 4 ) )[0] )
	jdwp = struct.unpack( '>II', data.read( 8 ) )
	vm_version = data.read( struct.unpack( '>I', data.read( 4 ) )[0] )
	vm_name = data.read( struct.unpack( '>I', data.read( 4 ) )[0] )
	print '%s (%s)\nJDWP %d.%d; JRE %s' % ( description, vm_name, jdwp[0], jdwp[1],vm_version )

def main():
	parser = argparse.ArgumentParser( description='Debug thyself some Java' )	
	# We'll stick to GNU-style options for now
	parser.add_argument(
		'--attach',
		metavar='ADDRESS',
		help='attach to a running VM at the specified address using standard connector',
		required=True,
	)
	
	attach( parser.parse_args().attach ) # Raises exceptions

if __name__ == '__main__':
	main()
