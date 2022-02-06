__author__ = 'Mahmud'


def enable_map(original_class):
    get_map_view_data = getattr(original_class, "get_map_view_data", None)
    if not callable(get_map_view_data):
        raise Exception(str(original_class) + " is decorated with 'enable_map' but does not implement 'get_map_view_data(self, **kwargs)'")
    return original_class