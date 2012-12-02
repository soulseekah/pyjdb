from jdwp.responses.base import ResponsePacket

import struct
import StringIO

class VersionResponse( ResponsePacket ):
	"""Returns the JDWP version implemented by the target VM. The version string format is implementation dependent."""	

	def __init__( self, data ):
		self.description = None
		self.jdwp = None
		self.vm_version = None
		self.vm_name = None
		super( self.__class__, self ).__init__( data )
		self.parse( data )

	def parse( self, data ):
		"""
		string description  Text information on the VM version
		int    jdwpMajor    Major JDWP Version number
		int    jdwpMinor    Minor JDWP Version number
		string vmVersion    Target VM JRE version, as in the java.version property
		string vmName       Target VM name, as in the java.vm.name property
		"""

		super( self.__class__, self ).parse( data )

		data = StringIO.StringIO( self.data )
		self.description = data.read( struct.unpack( '>I', data.read( 4 ) )[0] )
		self.jdwp = struct.unpack( '>II', data.read( 8 ) )
		self.vm_version = data.read( struct.unpack( '>I', data.read( 4 ) )[0] )
		self.vm_name = data.read( struct.unpack( '>I', data.read( 4 ) )[0] )

class AllClassesResponse( ResponsePacket ):
	"""Returns reference types for all classes currently loaded by the target VM."""

	def __init__( self, data, vm ):
		self.classes = []
		super( self.__class__, self ).__init__( data )
		self.parse( data, vm )

	def parse( self, data, vm ):
		"""
		int classes Number of reference types that follow.
		Repeated classes times:
			byte            refTypeTag Kind of following reference type.
			referenceTypeID typeID     Loaded reference type
			string          signature  The JNI signature of the loaded reference type
			int             status     The current class status.
		"""

		super( self.__class__, self ).parse( data )

		data = StringIO.StringIO( self.data )

		num_classes = struct.unpack( '>I', data.read( 4 ) )[0]

		from jdwp.misc import TypeTagConstants, ClassStatusConstants, JavaClass

		for i in xrange( num_classes ):
			jclass = JavaClass()
			jclass.type = TypeTagConstants.get( ord( data.read( 1 ) ), None )
			id = data.read( vm.reference_size )
			if ( vm.reference_size == 8 ):
				jclass.id = struct.unpack( '>q', id )[0]
			else:
				raise NotImplementedError()
			jclass.signature = data.read( struct.unpack( '>I', data.read( 4 ) )[0] )
			status = struct.unpack( '>I', data.read( 4 ) )[0]
			if jclass.type in ( 'CLASS', 'INTERFACE' ):
				statuses = [ _status for code, _status in ClassStatusConstants.items() if code & status ]
				jclass.status = statuses
			self.classes.append( jclass )

class AllClassesWithGenericResponse( ResponsePacket ):
	"""Returns reference types for all classes currently loaded by the target VM. Both the JNI signature and the generic signature are returned for each class."""

	def __init__( self, data, vm ):
		self.classes = []
		super( self.__class__, self ).__init__( data )
		self.parse( data, vm )

	def parse( self, data, vm ):
		"""
		int classes Number of reference types that follow.
		Repeated classes times:
			byte            refTypeTag       Kind of following reference type.
			referenceTypeID typeID           Loaded reference type
			string          signature        The JNI signature of the loaded reference type
			string          genericSignature The generic signature of the loaded reference type or an empty string if there is none. 
			int             status           The current class status.
		"""

		super( self.__class__, self ).parse( data )

		data = StringIO.StringIO( self.data )

		num_classes = struct.unpack( '>I', data.read( 4 ) )[0]

		from jdwp.misc import TypeTagConstants, ClassStatusConstants, JavaClass

		for i in xrange( num_classes ):
			jclass = JavaClass()
			jclass.type = TypeTagConstants.get( ord( data.read( 1 ) ), None )
			id = data.read( vm.reference_size )
			if ( vm.reference_size == 8 ):
				jclass.id = struct.unpack( '>q', id )[0]
			else:
				raise NotImplementedError()
			jclass.signature = data.read( struct.unpack( '>I', data.read( 4 ) )[0] )
			jclass.generic = data.read( struct.unpack( '>I', data.read( 4 ) )[0] )
			status = struct.unpack( '>I', data.read( 4 ) )[0]
			if jclass.type in ( 'CLASS', 'INTERFACE' ):
				statuses = [ _status for code, _status in ClassStatusConstants.items() if code & status ]
				jclass.status = statuses
			self.classes.append( jclass )

class IDSizesResponse( ResponsePacket ):
	"""Returns the sizes of variably-sized data types in the target VM. The returned values indicate the number of bytes used by the identifiers in command and reply packets."""

	def __init__( self, data ):
		self.field = None
		self.method = None
		self.object = None
		self.reference = None
		self.frame = None
		super( self.__class__, self ).__init__( data )
		self.parse( data )

	def parse( self, data ):
		"""
		int fieldIDSize         fieldID size in bytes
		int methodIDSize        methodID size in bytes
		int objectIDSize        objectID size in bytes
		int referenceTypeIDSize referenceTypeID size in bytes
		int frameIDSize         frameID size in bytes
		"""

		super( self.__class__, self ).parse( data )

		self.field, self.method, self.object, \
			self.reference, self.frame = struct.unpack( '>IIIII', self.data )
