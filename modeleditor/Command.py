from BufferFactory import *
from Utils import *

class Command:

	ARG_NO = 0
	def __init__(self, aReceiver, *args):
		"""
		checks and stores arguments 	
		after a buffer is passed to a Command, it shouldnt be 
		changed by other classes
		"""
		self.theArgs = copyValue( args)
		self.theReceiver = aReceiver
		self.executed = False
		self.theReverseCommandList = None

	def reset( self ):
		self.executed = False
		self.theReverseCommandList = None
	

	def execute(self):
		"""
		executes stored command
		can only be executed once
		returns True if successful
		returns False if command is non executable
		"""
		if self.isExecutable() and not self.isExecuted():

			self.createReverseCommand()
			if self.do():
				self.executed = True
			else:
				raise Exception("%s command failed.\n Arguments: %s"%(self.__class__.__name__, self.thaArgs) )
				self.theReverseCommandList = None



	def isExecuted(self):
		return self.executed



	def isExecutable(self):
		return  self.checkArgs()


	def getReverseCommandList(self):
		"""
		creates and returns a reverse commandlist with Buffers
		can only be called after execution
		"""
		return self.theReverseCommandList


	def checkArgs( self ):
		"""
		return True if self.Args are valid for this command
		"""

		if len(self.theArgs) != self.ARGS_NO :

			return False
		return True


	def do(self):
		"""
		perform command
		return True if successful
		"""
		return True

	def createReverseCommand(self):
		"""
		create  reverse command instance(s) and store it in a list as follows:
		"""
		self.theReverseCommandList = [ Command( self.theReceiver, [] ) ]

	def getAffectedObject( self ):
		if self.executed:
			return self.getAffected()
		else:
			return ( None, None )

	def getAffected( self ):
		return ( None, None )
	

class ModelCommand( Command ):

	"""
	contains the command name and the buffer needed to execute it
	can execute the command which can be:
	"""

	def checkArgs( self ):

		if not Command.checkArgs(self):

			return False

		if type( self.theReceiver) == type(self):

			if self.theReceiver.__class__.__name__ == 'ModelEditor':


				self.theModel = self.theReceiver.getModel()
				self.theBufferFactory = BufferFactory ( self.theModel )
				self.theBufferPaster = BufferPaster ( self.theModel )

				return True

		return False



	def isFullPNExist( self, aFullPN ):

		# first check whether FullID exists
		aFullID = getFullID( aFullPN )
		if not self.theModel.isEntityExist(aFullID ):
			return False
		propertyList = self.theModel.getEntityPropertyList( aFullID )
		if getPropertyName( aFullPN ) not in propertyList:
			return False
		return True

