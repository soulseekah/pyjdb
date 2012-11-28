from jdwp.responses.base import ResponsePacket

import struct
import StringIO

class VersionResponse( ResponsePacket ):
	"""Returns the JDWP version implemented by the target VM. The version string format is implementation dependent."""	

	def __init__( self ):
		super( self )
		self.description = None
		self.jdwp = None
		self.vm_version = None
		self.vm_name = None

	@staticmethod
	def parse( data ):
		"""
		string	description		Text information on the VM version 
		int		jdwpMajor		Major JDWP Version number 
		int		jdwpMinor		Minor JDWP Version number 
		string	vmVersion		Target VM JRE version, as in the java.version property 
		string	vmName			Target VM name, as in the java.vm.name property
		"""

		response = ResponsePacket.parse( data )

		data = StringIO.StringIO( response.data )
		response.description = data.read( struct.unpack( '>I', data.read( 4 ) )[0] )
		response.jdwp = struct.unpack( '>II', data.read( 8 ) )
		response.vm_version = data.read( struct.unpack( '>I', data.read( 4 ) )[0] )
		response.vm_name = data.read( struct.unpack( '>I', data.read( 4 ) )[0] )

		return response
