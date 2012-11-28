import argparse
import socket
import cmd

class PyJDBCmd( cmd.Cmd ):

	"""The main debugging command line"""
	def __init__( self, s ):
		cmd.Cmd.__init__( self )

		self.s = s
		self.prompt = '> '
		self.ruler = ''
	
	def default( self, line ):
		print 'Unrecognized command: \'%s\'. Try help...' % line
	
	def do_version( self, args ):
		"""print version information"""
		# Get JVM version
		from jdwp.commands.virtualmachine import VersionCommand
		from jdwp.responses.virtualmachine import VersionResponse

		command = VersionCommand()
		self.s.send( command.assemble() )
		response = VersionResponse.parse( self.s.recv( 128 ) )

		print '%s (%s)\nJDWP %d.%d; JRE %s' % \
			( response.description, response.vm_name,
			response.jdwp[0], response.jdwp[1], response.vm_version )
	
	def help_help( self ):
		print '...uhm, really?'
	
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

	# Start interactive command loop
	PyJDBCmd( s ).cmdloop()

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
