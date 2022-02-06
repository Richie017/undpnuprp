from collections import OrderedDict

INTERVENTION_TYPES = [
    'Single pit latrine', 'Twin pit latrine', 'Community Latrine', 'Septic Tank', 'Deep Tubewell',
    'Shallow Tubewell', 'Deepset Tubewell', 'Deep tubewell with submersible pump', 'Tubewell Platforms',
    'Water Reservoirs', 'Piped water supply', 'Bathroom', 'Footpath', 'Stair', 'Drain and/or Culvert',
    'Drain Slab and/or Road Slab', 'Market Shade', 'Building Contracts (Community Resource Center)',
    'Solar Street light', 'Non-solar Street light', 'FSM system', 'Garbage Management', 'Dustbin',
    'Rain Water Harvesting', 'Ground water recharging', 'Embankment cum Road', 'Multipurpose Use Center', 'Road',
    'Culvert Railing', 'Crossing Bridge',
]

WATER_INTERVENTION_TYPES = [
    'Deep Tubewell', 'Shallow Tubewell', 'Deepset Tubewell',
    'Deep tubewell with submersible pump', 'Tubewell Platforms', 'Water Reservoirs',
    "Bathroom",
]

MANDATORY_LENGTH_INTERVENTION_TYPES = [
    'Footpath', 'Road', 'Embankment cum Road', 'Stair',
    'Drain and/or Culvert', 'Drain Slab and/or Road Slab',
    'Culvert Railing', 'Crossing Bridge',
]

SANITATION_INTERVENTION_TYPES = ["Single pit latrine", "Twin pit latrine", "Community Latrine", "Septic Tank"]

DRINKING_WATER_SOURCES = ['Piped into dwelling', 'Piped into yard or plot', 'Public tap/standpipe', 'Tubewell/borehole',
                          'Protected well', 'Unprotected well', 'Protected spring', 'Unprotected spring', 'Rainwater',
                          'Tanker-truck', 'Cart with small tank/drum',
                          'Surface water (river, stream, dam, lake, pond, canal, irrigation channel)', 'Bottled Water']

SANITATION_FACILITY_TYPES = ['Pit latrine with slab', 'Flush to septic tank or piped sewer system or pit or drainage',
                             'Pit latrine without slab / open pit', 'Ventilated Improved Pit latrine (VIP) ',
                             'Hanging toilet/hanging latrine', 'Composting toilet', 'Bucket',
                             'Flush to unknown place/not sure/DK where', 'No facilities or bush or field', 'Other']

WATER_COLLECTION_TIME_OPTIONS = ['On-Premise', '5-10 minutes', '11-20 minutes', '21-30 minutes', 'More than 30 minutes']

DRAINAGE_INTERVENTION_TYPES = ['Drain and/or Culvert', 'Drain Slab and/or Road Slab']
FOOTPATH_INTERVENTION_TYPES = [
    'Footpath', 'Stair', 'Embankment cum Road',
    'Road', 'Culvert Railing', 'Crossing Bridge',
]
GARBAGE_MANAGEMENT_INTERVENTION_TYPES = ['Garbage Management', 'Dustbin']
SOLAR_STREETS_INTERVENTION_TYPES = ['Solar Street light', 'Non-solar Street light']
COMMUNITY_RESOURCE_INTERVENTION_TYPES = ['Building Contracts (Community Resource Center)', 'Multipurpose Use Center']
MARKET_INTERVENTION_TYPES = ['Market Shade']

INTERVENTION_CATEGORIES = [
    ('Water', WATER_INTERVENTION_TYPES + ['Piped water supply', 'Rain Water Harvesting', 'Ground water recharging']),
    ('Sanitation', SANITATION_INTERVENTION_TYPES + ['FSM system']),
    ('Drainage', DRAINAGE_INTERVENTION_TYPES),
    ('Footpath', FOOTPATH_INTERVENTION_TYPES),
    ('Garbage Management', GARBAGE_MANAGEMENT_INTERVENTION_TYPES),
    ('Solar Street light', SOLAR_STREETS_INTERVENTION_TYPES),
    ('Community Resource Center', COMMUNITY_RESOURCE_INTERVENTION_TYPES),
    ('Market Shade', MARKET_INTERVENTION_TYPES)
]
INTERVENTION_CATEGORIES = OrderedDict(INTERVENTION_CATEGORIES)
