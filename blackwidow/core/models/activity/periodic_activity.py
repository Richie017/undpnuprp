"""
    Created by tareq on 3/13/17
"""
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.extensions.clock import Clock

__author__ = 'Tareq'


class PeriodicBackgroundActivity(OrganizationDomainEntity):
    class Meta:
        abstract = True

    @classmethod
    def process(cls, time=None):
        if time is None:
            time = Clock.utcnow().timestamp() * 1000
        cls.generate(time=time)

    @classmethod
    def generate(cls, time=None):
        return True
