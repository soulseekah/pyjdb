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
from jdwp.events import EventKindConstants
from utils import UniqueDict

class PyJDBCmd( cmd.Cmd ):
	"""The main debugging command line"""

	def __init__( self, s ):
		cmd.Cmd.__init__( self )

		self.s = s
		self.prompt_default = '> '
		self.prompt = self.prompt_default
		self.ruler = ''

		# Start the socket read loop, responses and events will come in
		self.callbacks = UniqueDict( { '_lock': threading.Lock() } )
		# Also maintain a list of event subscribers
		self.event_listeners = { '_lock': threading.Lock() }
		self.event_listeners.update( { k: {} for k in EventKindConstants.keys() if isinstance( k, int ) } )
		# Maintain a deferred packet list and init state
		self.initted = False
		self.deferred = []

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

			self.initted = True
			for packet in self.deferred:
				self.received( packet )
				self.deferred = []

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
			return cmd.Cmd.onecmd( self, line )
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
			if not self.initted:
				self.deferred.append( data )
				return # Take care of later, we have not initialized yet
				# ...in particular, we require VM IDSizes

			# This is assumed to be an automatically generated Event
			# all Events are delivered inside a CompositeEvent packet
			from jdwp.events import CompositeEvent
			composite = CompositeEvent( data, self.vm )
			for event in composite.events:
				self.lock()
				print '* received EventType.%s' % EventKindConstants[event.kind]
				self.unlock()
				for listener in self.event_listeners[ event.kind ]:
					listener( event ) # Notify all listeners for this event kind
			return
		with self.callbacks['_lock']:
			callback = self.callbacks.get( response_id, None )
			if callback:
				del self.callbacks[response_id] # Pop it off
		if callback:
			if isinstance( callback, tuple ):
				callback[0]( self, data, **callback[1] )
			else:
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
		"""List currently known classes, takes an optional filter argument"""

		from jdwp.commands.virtualmachine import AllClassesWithGenericCommand
		from jdwp.responses.virtualmachine import AllClassesWithGenericResponse

		def print_classes( self, data, args=None ):
			response = AllClassesWithGenericResponse( data, self.vm )

			for classname in sorted( [ str( classname ) for classname in response.classes ] ):
				if not args or args in classname:
					print classname # Filter things out

			self.unlock()

		command = AllClassesWithGenericCommand()
		with self.callbacks['_lock']:
			self.callbacks[command.id] = ( print_classes, { 'args': args } )
		self.lock()
		self.s.send( command.assemble() )
	
	def do_threads( self, args ):
		"""List threads, optionally filtered by threadgroup"""

		from jdwp.commands.virtualmachine import AllThreadsCommand
		from jdwp.responses.virtualmachine import AllThreadsResponse

		from jdwp.misc import JavaThread
		threads = []
		threads_to_process = []
		release_lock = threading.Lock()

		from jdwp.commands.threadreference import NameCommand
		from jdwp.responses.threadreference import NameResponse
		from jdwp.commands.threadreference import StatusCommand
		from jdwp.responses.threadreference import StatusResponse

		from jdwp.misc import ThreadStatusConstants

		def print_threads( self, data, args=None ):
			response = AllThreadsResponse( data, self.vm )
			with release_lock:
				threads_to_process.extend( response.ids )

			# Retrieve all thread data available for each thread
			for thread_id in response.ids:
				thread = JavaThread( thread_id )

				command = NameCommand( thread.id, self.vm )
				with self.callbacks['_lock']:
					self.callbacks[command.id] = ( get_thread_name, { 'thread': thread } )
				self.s.send( command.assemble() )
			
		def get_thread_name( self, data, thread ):
			response = NameResponse( data )
			thread.name = response.name

			command = StatusCommand( thread.id, self.vm )
			with self.callbacks['_lock']:
				self.callbacks[command.id] = ( get_thread_status, { 'thread': thread } )
			self.s.send( command.assemble() )

		def get_thread_status( self, data, thread ):
			response = StatusResponse( data )
			thread.status = response.status
		
			# When all has been acquired
			with release_lock:
				threads.append( thread )
				threads_to_process.pop() # Decrease the number of threads to process
				if not len( threads_to_process ):
					for thread in threads:
						status = ThreadStatusConstants.get( thread.status, 'unknown' )
						print '%s ( %s ) %s' % ( thread.name, hex( thread.id )[:-1], status )
					self.unlock()

		command = AllThreadsCommand()
		with self.callbacks['_lock']:
			self.callbacks[command.id] = ( print_threads, { 'args': args } )
		self.lock()
		self.s.send( command.assemble() )

	def do_exit( self, args ):
		"""Exit debugger"""
		self.active = False
		self.reader.join()
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
	except Exception as e:
		# cm.do_exit( None )
		raise e
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
