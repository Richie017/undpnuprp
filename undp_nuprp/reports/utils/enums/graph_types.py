"""
    Created by tareq on 3/13/17
"""
from enum import Enum

__author__ = 'Tareq'


class GraphTypeEnum(Enum):
    FlatHtml = 'none'
    PieChart = 'pie'
    ColumnChart = 'column'
    StackedColumnChart = 'stacked-column'
    ScatterChart = 'scatter'
    HorizontalBarChart = 'horizontal-bar'
    StackedBarChart = 'stacked-bar'


class DataTableConfigEnum(Enum):
    DataTable = "TABLE"
