__author__ = 'Mahmud'


def expose_api(url_prefix, serializer=None):
    def expose_api(original_class):
        # orig_get_serializer = original_class.get_serializer
        #
        # def get_serializer():
        #     if original_class._serializer is not None:
        #         module = original_class._serializer[:original_class._serializer.rfind('.')]
        #         s_class_name = original_class._serializer[original_class._serializer.rfind('.') + 1:]
        #         return getattr(importlib.import_module(module), s_class_name)
        #     return orig_get_serializer()
        #
        # original_class.get_serializer = get_serializer
        original_class._url_prefix = url_prefix
        original_class._serializer = serializer
        return original_class
    return expose_api
