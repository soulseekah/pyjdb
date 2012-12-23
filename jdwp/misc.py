"""A temporary home for various classes that we don't know where to put for now"""

import StringIO

class VM( object ):
	"""Simple container to hold target JVM information, like versions, sizes, etc."""

	def __init__( self ):
		self.description = None
		self.jdwp = None
		self.version = None
		self.name = None

		self.field_size = None
		self.method_size = None
		self.object_size = None
		self.reference_size = None
		self.frame_size = None

class JavaClass( object ):
	"""Simple container for class objects and utitlity functions"""

	def __init__( self ):
		self.type = None
		self.signature = None
		self.generic = None
		self.id = None
		self.status = None
	
	def __str__( self ):
		"""Return a humanly-readable string for this class signature"""
		if not self.signature:
			return None

		signature = StringIO.StringIO( self.signature.replace( '/', '.' ) )
		is_array = ''
		while True: # Gobble up the type signature
			type_signature = signature.read( 1 )
			if type_signature == '[':
				is_array += '[]' # Will append later
				continue
			break

		# Expand the type signature
		type_signature = {
				'L': '', # Fully-qualified class
				'Z': 'boolean',	'B': 'byte', 'C': 'char', 'S': 'short',
				'I': 'int',	'J': 'long', 'F': 'float', 'D': 'double',
			}.get( type_signature, '' )

		signature = signature.read().replace( ';', '' ) # Read the rest

		return type_signature + signature + is_array
	
	def __unicode__( self ):
		return self.__str__( self )

class JavaThread( object ):
	"""Simple container for thread objects and utility functions"""

	def __init__( self, id=None ):
		self.id = id
		self.name = None
		self.group = None
		self.status = None
		self.suspended = None

# Contants
TypeTagConstants = {
	'CLASS': 1,
	'INTERFACE': 2,
	'ARRAY': 3,
} # And the reverse mapping
TypeTagConstants.update( { v: k for k, v in TypeTagConstants.items() } )

ClassStatusConstants = {
	'VERIFIED': 1,
	'PREPARED': 2,
	'INITIALIZED': 4,
	'ERROR': 8,
} # And the reverse mapping
ClassStatusConstants.update( { v: k for k, v in ClassStatusConstants.items() } )

ThreadStatusConstants = {
	'ZOMBIE': 0,
	'RUNNING': 1,
	'SLEEPING': 2,
	'MONITOR': 3,
	'WAIT': 4,  
} # And the reverse mapping
ThreadStatusConstants.update( { v: k for k, v in ThreadStatusConstants.items() } )

SuspendStatusConstants = {
	'SUSPEND_STATUS_SUSPENDED': 1,
} # And the reverse mapping
SuspendStatusConstants.update( { v: k for k, v in SuspendStatusConstants.items() } )
