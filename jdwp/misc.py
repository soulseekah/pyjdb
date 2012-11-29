"""A temporary home for various classes"""

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
