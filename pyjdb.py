import argparse
import socket
import select
import time
import sys
import cmd
import struct
import threading
import jdwp

class PyJDBCmd( cmd.Cmd ):
	"""The main debugging command line"""

	def __init__( self, s ):
		cmd.Cmd.__init__( self )

		self.s = s
		self.prompt_default = '> '
		self.prompt = self.prompt_default
		self.ruler = ''

		# Start the socket read loop, responses and events will come in
		self.callbacks = { '_lock': threading.Lock() }

		self.active = True
		self.reader = threading.Thread( target=self.readloop )
		self.reader.start()

	def readloop( self ):
		while self.active:
			# Read thread
			if not self.s in select.select( [ self.s ], [], [], 0.25 )[0]:
				continue

			length = self.s.recv( 4 ) # When we don't know how much to read
			data = self.s.recv( struct.unpack( '>I', length )[0] )
			data = length + data # Reconstruct as plain string

			try:
				self.received( data )
			except Exception as e: # A JDWP Exception
				print e
				sys.stdout.write( self.prompt_default )
				sys.stdout.flush()

	def received( self, data ):
		response_id = struct.unpack( '>I', data[4:8] )[0] # Get the ID
		if not response_id:
			# This is an Event
			# EventPacket.parse( data ), notify subscribers
			raise NotImplementedError( 'Received Event' )
		with self.callbacks['_lock']:
			callback = self.callbacks.get( response_id, None )
			if callback:
				del self.callbacks[response_id]
				callback( data )

	def default( self, line ):
		if line == 'EOF': return self.do_exit( line )

		print 'Unrecognized command: \'%s\'. Try help...' % line

	def do_version( self, args ):
		"""Print version information"""

		from jdwp.commands.virtualmachine import VersionCommand
		from jdwp.responses.virtualmachine import VersionResponse

		def print_version( data ):
			response = VersionResponse.parse( data )	
			print '%s (%s)\nJDWP %d.%d; JRE %s' % \
				( response.description, response.vm_name,
				response.jdwp[0], response.jdwp[1], response.vm_version )

			# TODO: just add lock() unlock() prompt when expecting
			self.prompt = self.prompt_default
			sys.stdout.write( self.prompt )
			sys.stdout.flush()

		command = VersionCommand()
		with self.callbacks['_lock']:
			self.callbacks[command.id] = print_version
		self.prompt = '' # Expecting a result any second now
		self.s.send( command.assemble() )

	def do_classes( self, args ):
		"""List currently known classes"""

		from jdwp.commands.virtualmachine import AllClassesCommand
		from jdwp.responses.virtualmachine import AllClassesResponse

		def print_classes( data ):
			response = AllClassesResponse.parse( data )

			print repr( response )

			# TODO: just add lock() unlock() prompt when expecting
			self.prompt = self.prompt_default
			sys.stdout.write( self.prompt )
			sys.stdout.flush()

		command = AllClassesCommand()
		with self.callbacks['_lock']:
			self.callbacks[command.id] = print_classes
		self.prompt = '' # Expecting a result any second now
		self.s.send( command.assemble() )

	def do_exit( self, args ):
		"""Exit debugger"""
		self.active = False
		return True # Stop
	def do_quit( self, args ):
		"""Exit debugger"""
		return self.do_exit( args )

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
	handshake = s.recv( 32 )

	if handshake != 'JDWP-Handshake':
		raise Exception( 'Unexpected JDWP handshake response: %s' % handshake )
	
	# Start interactive command loop
	try:
		cm = PyJDBCmd( s )
		cm.cmdloop()
	except KeyboardInterrupt:
		cm.do_exit( None )

	s.shutdown( socket.SHUT_RDWR )
	s.close()

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
