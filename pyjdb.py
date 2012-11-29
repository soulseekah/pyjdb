import argparse
import socket
import select
import time
import traceback
import sys
import cmd
import struct
import threading
import jdwp, jdwp.misc

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
		self.reader = threading.Thread( target=self.poll )
		self.reader.start()

		self.vm = jdwp.misc.VM()
		self.init_vm_info() # Get some data

	def init_vm_info( self ):
		"""Initializes target VM information"""
		from jdwp.commands.virtualmachine import VersionCommand
		from jdwp.responses.virtualmachine import VersionResponse

		def set_vm_version( self, data ):
			response = VersionResponse( data )	
			self.vm.description = response.description
			self.vm.name = response.vm_name
			self.vm.jdwp = response.jdwp
			self.vm.version = response.vm_version

		command = VersionCommand()
		with self.callbacks['_lock']:
			self.callbacks[command.id] = set_vm_version
		self.s.send( command.assemble() )

		from jdwp.commands.virtualmachine import IDSizesCommand
		from jdwp.responses.virtualmachine import IDSizesResponse
		
		def set_vm_sizes( self, data ):
			response = IDSizesResponse( data )
			self.vm.field_size = response.field
			self.vm.method_size = response.method
			self.vm.object_size = response.object
			self.vm.reference_size = response.reference
			self.vm.frame = response.frame

		command = IDSizesCommand()
		with self.callbacks['_lock']:
			self.callbacks[command.id] = set_vm_sizes
		self.s.send( command.assemble() )
	
	def lock( self ):
		self.prompt = ''

	def unlock( self ):	
		self.prompt = self.prompt_default
		sys.stdout.write( self.prompt_default )
		sys.stdout.flush()
	
	def onecmd( self, line ):
		try:
			cmd.Cmd.onecmd( self, line )
		except Exception as e:
			traceback.print_exc()

	def poll( self ):
		while self.active:
			# Read thread
			try:
				if not self.s in select.select( [ self.s ], [], [], 0.25 )[0]:
					continue
			except Exception:	
				self.active = False
				continue # Socket has gone away

			length = self.s.recv( 4 ) # When we don't know how much to read
			remaining = struct.unpack( '>I', length )[0] - 4 # 4 byte header
			data = ''
			while remaining: # Munch up all the data
				_buffer = self.s.recv( remaining )
				remaining = remaining - len( _buffer )
				data = data + _buffer
			data = length + data # Reconstruct as plain string

			try:
				self.received( data )
			except Exception as e: # A JDWP Exception
				traceback.print_exc()
				self.unlock()

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
				callback( self, data )

	def default( self, line ):
		if line == 'EOF': return self.do_exit( line )

		print 'Unrecognized command: \'%s\'. Try help...' % line

	def do_version( self, args ):
		"""Print version information"""
		print '%s (%s)\nJDWP %d.%d; JRE %s' % \
			( self.vm.description, self.vm.name,
			self.vm.jdwp[0], self.vm.jdwp[1], self.vm.version )

	def do_classes( self, args ):
		"""List currently known classes"""

		from jdwp.commands.virtualmachine import AllClassesCommand
		from jdwp.responses.virtualmachine import AllClassesResponse

		def print_classes( self, data ):
			response = AllClassesResponse( data, self.vm )

			for classname in response.classes:
				print classname['type'].lower(),
				print classname['signature'],
				print '0x%08x' % ( classname['id'] ),
				status = classname.get( 'status', None )
				if status:
					print ', '.join( status ).lower()
				else:
					print

			self.unlock()

		command = AllClassesCommand()
		with self.callbacks['_lock']:
			self.callbacks[command.id] = print_classes
		self.lock()
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
	except Exception:
		cm.do_exit( None )
		raise Exception
	finally:
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
