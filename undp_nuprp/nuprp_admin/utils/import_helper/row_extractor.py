__author__ = 'Tareq'


def extract_row(row, values, allow_merged_cell=False):
    """
    Extract individual raw of excel
    :param row: row of the excel file
    :param values: variables, where to assign the individual cell value
    :param allow_merged_cell: If true, then sets previous row value for an empty cell (considering merged cell)
    :return: return the tuple of variables populated with the values of cells of the row
    """
    for i in range(0, len(values)):
        if i >= len(row):
            return values
        if row[str(i)] is None:
            if not allow_merged_cell:
                values[i] = None
        else:
            values[i] = row[str(i)]
    return tuple(values)
