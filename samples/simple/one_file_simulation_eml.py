the_model_em = '''
<?xml version="1.0" ?>
<eml>
<stepper class="FixedODE1Stepper" id="DE1"/>
<system class="System" id="/">
<property name="StepperID">
<value>DE1</value>
</property>
<variable class="Variable" id="SIZE">
<property name="Value">
<value>1e-18</value>
</property>
</variable>
<variable class="Variable" id="S">
<property name="Value">
<value>1000000</value>
</property>
</variable>
<variable class="Variable" id="P">
<property name="Value">
<value>0</value>
</property>
</variable>
<variable class="Variable" id="E">
<property name="Value">
<value>1000</value>
</property>
</variable>
<process class="MichaelisUniUniFluxProcess" id="E">
<property name="VariableReferenceList">
<value>
<value>S0</value>
<value>:.:S</value>
<value>-1</value>
</value>
<value>
<value>P0</value>
<value>:.:P</value>
<value>1</value>
</value>
<value>
<value>C0</value>
<value>:.:E</value>
<value>0</value>
</value>
</property>
<property name="KmS">
<value>1</value>
</property>
<property name="KcF">
<value>10</value>
</property>
</process>
</system>
</eml>
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
duration = 1000
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
aDataFile = ECDDataFile( S_Logger.getData(0,2000,.5) )
aDataFile.setDataName( S_Logger.getName() )
aDataFile.setNote( '' )
aDataFile.save( 'S.ecd' )

#message('loading')
#aNewFile = ECDDataFile()
#aNewFile.load( 'S.ecd' )
#print aNewFile.getData()[:10]
