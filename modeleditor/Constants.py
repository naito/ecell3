from ConfirmWindow import *


# ModelStore constants

MS_STEPPER_CLASS = 0
MS_STEPPER_PROPERTYLIST = 1
MS_STEPPER_INFO = 2
MS_STEPPER_SYSTEMLIST = 'SystemList'
MS_STEPPER_PROCESSLIST = 'ProcessList'
MS_VARIABLE_PROCESSLIST = 'ProcessList'
MS_PROCESS_VARREFLIST = 'VariableReferenceList'

MS_PROPERTY_VALUE = 0
MS_PROPERTY_FLAGS = 1
MS_PROPERTY_TYPE = 2

MS_SETTABLE_FLAG = 0
MS_GETTABLE_FLAG = 1
MS_DELETEABLE_FLAG = 4

MS_VARREF_NAME = 0
MS_VARREF_FULLID = 1
MS_VARREF_COEF = 2


MS_SYSTEM_STEPPERID = 'StepperID'
MS_PROCESS_STEPPERID = 'StepperID'


MS_ENTITY_CLASS = 0
MS_ENTITY_PROPERTYLIST = 1
MS_ENTITY_PARENT = 2
MS_ENTITY_CHILD_SYSTEMLIST = 3
MS_ENTITY_CHILD_PROCESSLIST = 4
MS_ENTITY_CHILD_VARIABLELIST = 5
MS_ENTITY_INFO = 6

MS_SYSTEM_ROOT = 'System::/'



# DM constants
ECELL_PROPERTY_SETTABLE_FLAG = 0

DM_DESCRIPTION = "DESCRIPTION"
DM_ACCEPTNEWPROPERTY = "ACCEPTNEWPROPERTY"
DM_PROPERTYLIST ="PROPERTYLIST"

DM_PROPERTY_DEFAULTVALUE = "DEFAULTVALUE"
DM_PROPERTY_SETTABLE_FLAG = "SETTABLEFLAG"
DM_PROPERTY_GETTABLE_FLAG = "GETTABLEFLAG"
DM_PROPERTY_DELETEABLE_FLAG = "DELETEABLEFLAG"
DM_PROPERTY_TYPE = "TYPE"

DM_PROPERTY_STRING = "STRING"
DM_PROPERTY_MULTILINE = "MULTILINE"
DM_PROPERTY_NESTEDLIST = "NESTED_LIST"
DM_PROPERTY_INTEGER = "INTEGER"
DM_PROPERTY_FLOAT = "FLOAT"

DM_SYSTEM_CLASS = 'CompartmentSystem'
DM_SYSTEM_CLASS_OLD = 'System'

DM_VARIABLE_CLASS = 'Variable'



#message types
ME_PLAINMESSAGE = 0
ME_OKCANCEL = 1
ME_YESNO = 2
ME_WARNING = 3
ME_ERROR = 4

ME_RESULT_OK = OK_PRESSED
ME_RESULT_CANCEL = CANCEL_PRESSED

#propertyattributes
ME_GETTABLE_FLAG = MS_GETTABLE_FLAG
ME_SETTABLE_FLAG = MS_SETTABLE_FLAG
ME_DELETEABLE_FLAG = MS_DELETEABLE_FLAG

ME_ROOTID = 'System::/'

#varref indexes
ME_VARREF_NAME = 0
ME_VARREF_FULLID = 1
ME_VARREF_COEF = 2

#entity types
ME_SYSTEM_TYPE = "System"
ME_VARIABLE_TYPE = "Variable"
ME_PROCESS_TYPE = "Process"
ME_STEPPER_TYPE = "Stepper"
ME_PROPERTY_TYPE = "Property"

#special properties
ME_STEPPER_SYSTEMLIST = MS_STEPPER_SYSTEMLIST
ME_STEPPER_PROCESSLIST = MS_STEPPER_PROCESSLIST
ME_VARIABLE_PROCESSLIST = MS_VARIABLE_PROCESSLIST
ME_PROCESS_VARREFLIST = MS_PROCESS_VARREFLIST
ME_STEPPERID = MS_SYSTEM_STEPPERID

#undo
MAX_REDOABLE_COMMAND = 20

#ADCP flags
ME_ADD_FLAG = 0
ME_DELETE_FLAG = 1
ME_COPY_FLAG = 2
ME_PASTE_FLAG = 3
ME_EDIT_FLAG = 4
ME_BROWSE_FLAG = 5

ME_FLAGS_NO = 6

#varrefs
ME_VARREF_FULLID = 1

