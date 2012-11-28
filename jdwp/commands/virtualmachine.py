from jdwp.commands.base import CommandPacket

class VersionCommand( CommandPacket ):
	"""Returns the JDWP version implemented by the target VM. The version string format is implementation dependent."""

	command = 1 # Version
	command_set = 1 # VirtualMachine

	def __init__( self ):
		super( self.__class__, self ).__init__()

class AllClassesCommand( CommandPacket ):
	"""Returns reference types for all classes currently loaded by the target VM."""

	command = 3 # AllClasses
	command_set = 1 # VirtualMachine

	def __init__( self ):
		super( self.__class__, self ).__init__()
