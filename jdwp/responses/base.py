import struct
import socket

class ResponsePacket( object ):
	"""A Response Packet superclass"""

	def __init__( self ):
		self.length = 11 # Header
		self.id = None
		self.flags = None
		self.error = None
		self.data = None
		
	@staticmethod
	def parse( data ):
		"""Parses the header, data parsing is left up to the child"""

		response = ResponsePacket()

		response.length, response.id, response.flags, \
			response.error = struct.unpack( '>IIBH', data[:11] )
		response.data = data[11:]

		if response.error:
			raise Exception( ResponsePacket.strerr( response.error ) )

		return response

	@staticmethod
	def strerr( errno ):
		"""Returns descriptions for errors"""

		errors = {
			0: 'No error has occurred',
			10: 'Passed thread is null, is not a valid thread or has exited.',
			11: 'Thread group invalid.',
			12: 'Invalid priority.',
			13: 'If the specified thread has not been suspended by an event.',
			14: 'Thread already suspended.',
			15: 'Thread has not been started or is now dead.',
			20: 'If this reference type has been unloaded and garbage collected.',
			21: 'Invalid class.',
			22: 'Class has been loaded but not yet prepared.',
			23: 'Invalid method.',
			24: 'Invalid location.',
			25: 'Invalid field.',
			30: 'Invalid jframeID.',
			31: 'There are no more Java or JNI frames on the call stack.',
			32: 'Information about the frame is not available.',
			33: 'Operation can only be performed on current frame.',
			34: 'The variable is not an appropriate type for the function used.',
			35: 'Invalid slot.',
			40: 'Item already set.',
			41: 'Desired element not found.',
			50: 'Invalid monitor.',
			51: 'This thread doesn\'t own the monitor.',
			52: 'The call has been interrupted before completion.',
			60: 'The virtual machine attempted to read a class file and determined that the file is malformed or otherwise cannot be interpreted as a class file.',
			61: 'A circularity has been detected while initializing a class.',
			62: 'The verifier detected that a class file, though well formed, contained some sort of internal inconsistency or security problem.',
			63: 'Adding methods has not been implemented.',
			64: 'Schema change has not been implemented.',
			65: 'The state of the thread has been modified, and is now inconsistent.',
			66: 'A direct superclass is different for the new class version, or the set of directly implemented interfaces is different and canUnrestrictedlyRedefineClasses is false.',
			67: 'The new class version does not declare a method declared in the old class version and canUnrestrictedlyRedefineClasses is false.',
			68: 'A class file has a version number not supported by this VM.',
			69: 'The class name defined in the new class file is different from the name in the old class object.',
			70: 'The new class version has different modifiers and and canUnrestrictedlyRedefineClasses is false.',
			71: 'A method in the new class version has different modifiers than its counterpart in the old class version and and canUnrestrictedlyRedefineClasses is false.',
			99: 'The functionality is not implemented in this virtual machine.',
			100: 'Invalid pointer.',
			101: 'Desired information is not available.',
			102: 'The specified event type id is not recognized.',
			103: 'Illegal argument.',
			110: 'The function needed to allocate memory and no more memory was available for allocation.',
			111: 'Debugging has not been enabled in this virtual machine. JVMTI cannot be used.',
			112: 'The virtual machine is not running.',
			113: 'An unexpected internal error has occurred.',
			115: 'The thread being used to call this function is not attached to the virtual machine. Calls must be made from attached threads.',
			500: 'object type id or class tag.',
			502: 'Previous invoke not complete.',
			503: 'Index is invalid.',
			504: 'The length is invalid.',
			506: 'The string is invalid.',
			507: 'The class loader is invalid.',
			508: 'The array is invalid.',
			509: 'Unable to load the transport.',
			510: 'Unable to initialize the transport.',
			511: 'Unknown',
			512: 'The count is invalid.',
		}

		return errors.get( errno, 'Unknown' )
