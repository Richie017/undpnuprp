from blackwidow.core.models.contracts.base import DomainEntity
from blackwidow.engine.decorators.enable_trigger import enable_trigger
from blackwidow.engine.decorators.utility import decorate

__author__ = 'Mahmud'

from django.db import models
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

@decorate(enable_trigger)
class EmailAddress(DomainEntity):
    email = models.EmailField(max_length=100)
    is_primary = models.BooleanField(default=0)

    def load_initial_data(self, **kwargs):
        super().load_initial_data(**kwargs)
        self.email = "test" + str(kwargs['index']) + '@email.com'

    def __str__(self):
        return self.email

    @classmethod
    def get_serializer(cls):
        ss = DomainEntity.get_serializer()

        class Serializer(ss):
            class Meta(DomainEntity.Meta):
                model = cls
                fields = ( 'id', 'code', 'email','date_created' )
        return Serializer

    @staticmethod
    def is_email_valid(self, email):
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False


