__author__ = 'Tareq'


def bw_special_chars(name):
    name = name.replace('render_', '')
    name = name.replace('__or__', '/')
    name = name.replace('__percent__', '%')
    name = name.replace('__bracket_start__', '(')
    name = name.replace('__bracket_close__', ')')
    name = name.replace('__question__', '?')
    name = name.replace('__exclamation__', '!')
    name = name.replace('__hyphen__', '-')
    return name
