import StringIO
import struct

EventKindConstants = {
	'VM_DISCONNECTED': 100,
	'SINGLE_STEP': 1,	  
	'BREAKPOINT': 2,	  
	'FRAME_POP': 3,	  
	'EXCEPTION': 4,	  
	'USER_DEFINED': 5,	  
	'THREAD_START': 6,	  
	'THREAD_END': 7,	  
	'CLASS_PREPARE': 8,	  
	'CLASS_UNLOAD': 9,	  
	'CLASS_LOAD': 10,	  
	'FIELD_ACCESS': 20,	  
	'FIELD_MODIFICATION': 21,	  
	'EXCEPTION_CATCH': 30,	  
	'METHOD_ENTRY': 40,	  
	'METHOD_EXIT': 41,	  
	'VM_INIT': 90,	  
	'VM_DEATH': 99,
} # Add aliases and reverse map
EventKindConstants['VM_START'] = EventKindConstants['VM_INIT']
EventKindConstants['THREAD_DEATH'] = EventKindConstants['THREAD_END']
EventKindConstants.update( { v: k for k, v in EventKindConstants.items() } )

class CompositeEvent( object ):
	"""Several events may occur at a given time in the target VM. For example, there may be more than one breakpoint request for a given location or you might single step to the same location as a breakpoint request. These events are delivered together as a composite event. For uniformity, a composite event is always used to deliver events, even if there is only one event to report."""

	def __init__( self, data, vm ):
		"""Parsing of data structure endeavors to be in accord with the http://docs.oracle.com/javase/1.5.0/docs/guide/jpda/jdwp/jdwp-protocol.html#JDWP_Event_Composite manuscript"""

		# A composite event comes with Command headers, not Response ones
		self.length, self.id, self.flags, \
			self.commandset, self.command = struct.unpack( '>IIBBB', data[:11] )
		self.data = data[11:]

		self.events = []

		data = StringIO.StringIO( self.data )
		self.suspend_policy = data.read( 1 ) # Not exactly sure what this is
		self.count = struct.unpack( '>I', data.read( 4 ) )[0]
		
		for i in xrange( self.count ):
			self.events.append( self.make_event( data, vm ) )
	
	def make_event( self, data, vm ):
		"""An Event object factory that reads a stream and constructs an event of EventKind."""

		kind = ord( data.read( 1 ) )
		# Dynamically construct an Event from string and pass in the data
		event = globals()[ EventKindConstants[kind].title().replace( '_', '' ) + 'Event' ]( data, vm )
		event.kind = kind
		return event

class Event( object ):
	def __init__( self, data, vm ):
		self.kind = None
		self.id = struct.unpack( '>I', data.read( 4 ) )[0]
		thread = data.read( vm.object_size )
		if ( vm.object_size == 8 ):
			self.thread_id = struct.unpack( '>q', thread )[0]
		else:
			raise NotImplementedError
		
class VmStartEvent( Event ):
	"""Notification of initialization of a target VM. This event is received before the main thread is started and before any application code has been executed. Before this event occurs a significant amount of system code has executed and a number of system classes have been loaded. This event is always generated by the target VM, even if not explicitly requested."""

	def __init__( self, data, vm ):
		"""
		int      requestID Request that generated event (or 0 if this event is automatically generated. 
		threadID thread    Initial thread 
		"""
		super( self.__class__, self ).__init__( data, vm )

class VmInitEvent( VmStartEvent ):
	"""Alias for VmStartEvent"""
	pass
