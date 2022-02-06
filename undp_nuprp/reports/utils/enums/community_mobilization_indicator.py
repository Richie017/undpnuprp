from enum import Enum

__author__ = "Shama"


class CommunityMobilizationIndicatorEnum(Enum):
    PGMemberEnum = 'pgmember'
    PGNumberEnum = 'pgnumber'
    CDCNumberEnum = 'cdcnumber'
    CDCClusterNumberEnum = 'cdcclusternumber'
    AllPGMemberEnum = 'allpgmember'
    AllPGNumberEnum = 'allpgnumber'
    AllCDCNumberEnum = 'allcdcnumber'
    AllCDCClusterNumberEnum = 'allcdcclusternumber'