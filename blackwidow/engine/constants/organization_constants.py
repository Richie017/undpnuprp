from blackwidow.engine.validators.configvalidators import *

BW_ORGANIZATION_DBLOCK = 'lock_database'
BW_ORGANIZATION_DBLOCK_TILL = 'lock_database_till'

BW_ORGANIZATON_SETTINGS = dict(
    allow_duplicates=False,
    keys=list())

BW_ORGANIZATON_SETTINGS['keys'].append(dict(
    name=BW_ORGANIZATION_DBLOCK,
    display='Lock Database',
    type='boolean',
    default='False',
    range=set(['True', 'False']),
    validator=BooleanValidator,
    dbkey=BW_ORGANIZATION_DBLOCK
))

BW_ORGANIZATON_SETTINGS['keys'].append(dict(
    name=BW_ORGANIZATION_DBLOCK_TILL,
    display='Lock Database Till',
    type='datetime',
    default='01/01/1970',
    validator=DateTimeValidator,
    allowFutureDate=False,
    allowPastDate=True,
    allowCurrentDate=False,
    dbkey=BW_ORGANIZATION_DBLOCK_TILL
))



