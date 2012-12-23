class UniqueDict( dict ):
	def __setitem__( self, key, value ):
		if key not in self:
			return dict.__setitem__( self, key, value )
		raise KeyError( 'Key already exists' )

