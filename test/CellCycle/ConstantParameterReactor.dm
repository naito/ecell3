
CLASSNAME = 'ConstantParameterReactor'
BASECLASS = 'Reactor'
PROPERTIES = []

PROTECTED_AUX = '''
  Real _value;
'''

defineMethod( 'initialize', '''
//
''' )

defineMethod( 'react', '''
//  _value = getSuperSystem()->getStepper()->getStepInterval();
  _value = getStepper()->getStepInterval();
  setActivity( _value );
''' )

