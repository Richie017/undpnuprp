from django.db.models.base import ModelBase

__author__ = 'Mahmud'


def merge_list_to_dict(a):
    new_a = dict()
    items = []
    for _a in a:
        if isinstance(_a, dict):
            for x in _a:
                if x in new_a:
                    merge(new_a[x], _a[x])
                else:
                    new_a[x] = _a[x]
        else:
            items.append(_a)
    return new_a if len(items) == 0 else items


def merge(a, b):
    for key in b:
        if isinstance(key, str) and key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key])
            elif isinstance(a[key], list) and isinstance(b[key], list):
                a[key] = merge(merge_list_to_dict(a[key]), merge_list_to_dict(b[key]))
            else:
                pass
        else:
            if isinstance(key, str) and isinstance(b[key], list):
                a[key] = merge_list_to_dict(b[key])
            elif isinstance(key, ModelBase):
                if key not in a:
                    a.append(key)
            else:
                a[key] = b[key]
    return a