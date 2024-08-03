def thousand_separator(value):
    """
    :param value:
    :return: thousand separated representation of given value
    """
    try:
        return "{:,}".format(value)
    except:
        return value
