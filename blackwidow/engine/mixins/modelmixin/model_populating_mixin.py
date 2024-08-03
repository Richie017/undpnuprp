import random
import string

__author__ = 'Mahmud'


class ModelPopulatingMixin(object):
    def populate_demo(self, **kwargs):
        model_class = kwargs.pop('model_class')
        obj = model_class()
        fields = obj._meta.get_fields_with_model()
        for field in fields:
            x = field

    def generate_string(self, length=10):
        return ''.join(random.choice(string.ascii_letters) for _ in range(length))

    def generate_integer(self, length=3):
        return int(''.join(random.choice(string.digits) for _ in range(length)))

    def generate_decimal(self, length=2, decimal=2):
        return float(''.join(random.choice(string.digits) for _ in range(length)) + "." + ''.join(random.choice(string.digits) for _ in range(decimal)))
