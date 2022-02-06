__author__ = 'Mahmud'


class AuditableModelMixin(object):
    @classmethod
    def get_status_api_key(cls):
        return cls.__name__.lower()
