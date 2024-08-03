from enum import Enum

__author__ = "Shama"


class SavingsAndCreditIndicatorEnum(Enum):
    SCGMemberEnum = 'scgmember'
    SCGPercentEnum = 'scgpercent'
    SCGSavingEnum = 'saving'
    CumulativeSavingEnum = 'cumulativesaving'
    SCGLoanEnum = 'loan'

    CumulativeLoanEnum = 'cumulativeloan'
    CumulativeOutStandingLoanEnum = 'cumulativeoutstanding'
    SCGMoneyEnum = 'money'
    SCGOntimeEnum = 'ontime'
    SCGFundEnum = 'fund'
