__author__ = 'mahmudul'

import re

BW_first_cap_re = re.compile('(.)([A-Z][a-z]+)')
BW_all_cap_re = re.compile('([a-z0-9])([A-Z])')


def bw_titleize(name):
    s1 = BW_all_cap_re.sub(r'\1_\2', name)
    # title = "".join([a if a.isupper() else b for a, b in zip(s2, s2.title())])
    s_list = list(s1)
    s_list[0] = s_list[0].upper()
    s2 = "".join(s_list)
    return s2.replace(r'_', r' ')

def bw_compress_name(name):
    s1 = BW_first_cap_re.sub(r'\1_\2', name)
    s2 = BW_all_cap_re.sub(r'\1_\2', s1)
    title = "".join([a if a.isupper() else b for a, b in zip(s2, s2.title())])
    return title.replace(r' ', r'').replace('/', '_')


def bw_decompress_name(name):
    return bw_titleize(name.replace(r' ', r'').replace('_', '/')).replace('/ ', '/')
