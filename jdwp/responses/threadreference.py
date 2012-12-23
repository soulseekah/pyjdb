from jdwp.responses.base import ResponsePacket

import struct
import StringIO

class NameResponse( ResponsePacket ):
	"""Returns the thread name."""

	def __init__( self, data ):
		self.name = None
		super( self.__class__, self ).__init__( data )
		self.parse( data )

	def parse( self, data ):
		"""
		string threadName The thread name
		"""

		super( self.__class__, self ).parse( data )

		data = StringIO.StringIO( self.data )
		self.name = data.read( struct.unpack( '>I', data.read( 4 ) )[0] )

class StatusResponse( ResponsePacket ):
	"""Returns the current status of a thread."""

	def __init__( self, data ):
		self.status = None
		self.suspend = None
		super( self.__class__, self ).__init__( data )
		self.parse( data )

	def parse( self, data ):
		"""
		int threadStatus  One of the thread status codes
		int suspendStatus One of the suspend status codes
		"""

		super( self.__class__, self ).parse( data )

		data = StringIO.StringIO( self.data )
		self.status = struct.unpack( '>I', data.read( 4 ) )[0]
		self.suspend = struct.unpack( '>I', data.read( 4 ) )[0]
