"""A temporary home for various classes"""

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

# Some Contants
TypeTagConstants = {
	1: 'CLASS',
	2: 'INTERFACE',
	3: 'ARRAY'
}
ClassStatusConstants = {
	1: 'VERIFIED',
	2: 'PREPARED',
	4: 'INITIALIZED',
	8: 'ERROR'
}
