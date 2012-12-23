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

class AllThreadsCommand( CommandPacket ):
	"""Returns all thread IDs currently running in the target VM."""

	command = 4 # AllThreads
	command_set = 1 # VirtualMachine

	def __init__( self ):
		super( self.__class__, self ).__init__()

class IDSizesCommand( CommandPacket ):
	"""Returns the sizes of variably-sized data types in the target VM.The returned values indicate the number of bytes used by the identifiers in command and reply packets."""

	command = 7 # IDSizes
	command_set = 1 # VirtualMachine

	def __init__( self ):
		super( self.__class__, self ).__init__()

class AllClassesWithGenericCommand( CommandPacket ):
	"""Returns reference types for all classes currently loaded by the target VM. Both the JNI signature and the generic signature are returned for each class."""

	command = 20 # AllClassesWithGeneric
	command_set = 1 # VirtualMachine

	def __init__( self ):
		super( self.__class__, self ).__init__()
