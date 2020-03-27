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

message('saving S.ecd..')
message( 'Logger data:\n%s' % S_Logger.getData(0,2000,.5))
aDataFile = ECDDataFile( S_Logger.getData(0,2000,.5) )
aDataFile.setDataName( S_Logger.getName() )
aDataFile.setNote( '' )
message( 'ECD contents:\n%s' % aDataFile.getHeaderString())
message( '%s\n' % aDataFile.getData())
aDataFile.save( 'S.ecd' )

#message('loading')
#aNewFile = ECDDataFile()
#aNewFile.load( 'S.ecd' )
#print aNewFile.getData()[:10]
