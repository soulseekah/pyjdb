from jdwp.commands.base import CommandPacket
import struct

class NameCommand( CommandPacket ):
	"""Returns the thread name."""

	command = 1 # Name
	command_set = 11 # ThreadReference

	def __init__( self, thread_id, vm ):
		"""
		threadID thread The thread object ID 
		"""

		super( self.__class__, self ).__init__()

		if ( vm.reference_size == 8 ):
			self.data = struct.pack( '>q', thread_id )
		else:
			raise NotImplementedError()

		self.length = self.length + len( self.data )

class StatusCommand( CommandPacket ):
	"""Returns the current status of a thread."""

	command = 4 # Status
	command_set = 11 # ThreadReference

	def __init__( self, thread_id, vm ):
		"""
		threadID thread The thread object ID 
		"""

		super( self.__class__, self ).__init__()

		if ( vm.reference_size == 8 ):
			self.data = struct.pack( '>q', thread_id )
		else:
			raise NotImplementedError()

		self.length = self.length + len( self.data )
