import re

__author__ = 'Mahmud'


class CodedModelMixin(object):
    @classmethod
    def prefix(cls):
        return re.sub(r'[a-z\d]+|(?<=[A-Z])[A-Z\d]+', r'', cls.__name__)

    @classmethod
    def get_class_name(cls):
        return cls.__name__

    @property
    def code_prefix(self):
        return self.__class__.prefix()

    @classmethod
    def get_code_prefix(cls):
        return cls.prefix()

    @property
    def code_separator(self):
        return "-"

    @classmethod
    def generate_missing_codes(cls):
        try:
            missing_code_items = cls.objects.filter(code='').all()
            for missing_code_item in missing_code_items:
                missing_code_item.save()
        except:
            pass
