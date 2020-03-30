the_model_em = '''
#
# A very simple model with one michaelis-uni-uni reaction.
#

# Stepper ODEStepper( DE1 )
Stepper FixedODE1Stepper( DE1 )
{
	# no property
}

System System( / )
{
	StepperID	DE1;

	Variable Variable( SIZE )
	{
		Value	1e-18;
	}

	Variable Variable( S )
	{
		Value	1000000;
	}

	Variable Variable( P )
	{
		Value	0;
	}

	Variable Variable( E )
	{
		Value	1000;
	}

	Process MichaelisUniUniFluxProcess( E )
	{
		VariableReferenceList	[ S0 :.:S -1 ]
 					[ P0 :.:P 1 ]
					[ C0 :.:E 0 ];
		KmS	1;
		KcF	10;
	}


}
'''

# load the model
setModel( the_model_em, 'simple.em' )

# create stubs
S_Logger = createLoggerStub( 'Variable:/:S:Value' )
S_Logger.create()
S = createEntityStub( 'Variable:/:S' )


# print some values
message( 't= \t%s' % getCurrentTime() )
message( 'S:Value= \t%s' % S.getProperty( 'Value' ) )
message( 'S:MolarConc= \t%s' % S.getProperty( 'MolarConc' ) )
# run
duration = 2000
S_Logger.getData(0,2000,.5)
message( '\n' )
message( 'run %s sec.\n' % duration )
run( duration )


# print results
message( 't= \t%s' % getCurrentTime() )
message( 'S:Value= \t%s' % S.getProperty( 'Value' ) )
message( 'S:MolarConc= \t%s' % S.getProperty( 'MolarConc' ) )

message( '\n' )

from ecell.ECDDataFile import *

# message( 'Logger data:\n%s' % S_Logger.getData(0,2000,.5))
message( "\necell3-session>>> S_Logger_data = S_Logger.getData(0,2000,.5)" )
S_Logger_data = S_Logger.getData(0,2000,.5)
print( type( S_Logger_data ) )

message( '\necell3-session>>> type( S_Logger_data )' )
print( type( S_Logger_data ))

message( '\necell3-session>>> dir( S_Logger_data )' )
print( dir( S_Logger_data ))

#message( '\necell3-session>>> vars( S_Logger_data )' )
#print( vars( S_Logger_data ))

message( "\necell3-session>>> aDataFile = ECDDataFile( S_Logger_data )" )
aDataFile = ECDDataFile( S_Logger_data )

message( "\necell3-session>>> aDataFile.setDataName( S_Logger.getName() )" )
aDataFile.setDataName( S_Logger.getName() )

message( "\necell3-session>>> aDataFile.setNote( '' )" )
aDataFile.setNote( '' )

message( "\necell3-session>>> aDataFile.getHeaderString()" )
aDataFile.getHeaderString()

message( "\necell3-session>>> ecell3-session>>> aDataFile.getDataName()" )
aDataFile.getDataName()

message( "\necell3-session>>> aDataFile.getSizeOfColumn()" )
aDataFile.getSizeOfColumn()

message( "\necell3-session>>> aDataFile.getSizeOfLine()" )
aDataFile.getSizeOfLine()

message( "\necell3-session>>> theSimulator.getLoggerData('Variable:/:S:Value', 0, 500 )" )
theSimulator.getLoggerData('Variable:/:S:Value', 0, 500 )

message( '\necell3-session>>> type( aDataFile )' )
print( type( aDataFile ))

message( '\necell3-session>>> dir( aDataFile )' )
print( dir( aDataFile ))

#message( '\necell3-session>>> vars( aDataFile )' )
#print( vars( aDataFile ))

message( '\necell3-session>>> aDataFile.getData()' )
aDataFile.getData()
message( 'No return: succeeded.' )
message( '%s\n' % aDataFile.getData())

message( "\necell3-session>>> aDataFile.save( 'S.ecd' )" )
aDataFile.save( 'S.ecd' )

#message('loading')
#aNewFile = ECDDataFile()
#aNewFile.load( 'S.ecd' )
#print aNewFile.getData()[:10]
