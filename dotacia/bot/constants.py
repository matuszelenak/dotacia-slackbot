import re

COMMAND_DOTACIA = '/dotacia'


NUMBER_GIVE_TEMPLATE = re.compile('^give( +(?P<amount>[0-9]+)){0, 1}$')
NUMBER_REGISTER_TEMPLATE = re.compile('^register +(?P<number>[0-9]{17})( +(?P<priority>[1-5]))*$')
NUMBER_SET_PRIORITY_TEMPLATE = re.compile('^priority +(?P<priority>[1-5])$')
NUMBER_DISABLE_TEMPLATE = re.compile('^disable$')
NUMBER_ENABLE_TEMPLATE = re.compile('^enable$')
NUMBER_USE_TEMPLATE = re.compile('^use$')
