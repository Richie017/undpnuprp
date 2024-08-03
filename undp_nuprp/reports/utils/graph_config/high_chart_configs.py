"""
Created by tareq on 3/8/17
"""
__author__ = 'Tareq'


def apply_params(config, **params):
    for key, value in params.items():
        if key not in config.keys():
            config[key] = dict()
        part = config[key]
        if isinstance(value, dict):
            if isinstance(part, dict):
                config[key] = apply_params(part, **value)
            else:
                part = dict()
                part.update(**value)
        else:
            config[key] = value
    return config


def get_flat_html_config():
    return {
        'is_html': True
    }


def get_pie_chart_config(title, export_title, point_format=None):
    return {
        'chart': {
            'type': 'pie'
        },
        'title': {
            'text': title,
            'useHTML': True
        },
        'exporting': {
            'sourceWidth': 800,
            'sourceHeight': 400,

            'chartOptions': {
                'title': {
                    'text': export_title
                },
                'plotOptions': {
                    'series': {
                        'dataLabels': {
                            'enabled': True,
                            'useHTML': True,
                            'format': '<span class="datalabel" >{point.percentage:.0f} %</span>',
                            'distance': -40,
                            'color': 'rgb(102, 102, 102)',
                            'style': {
                                'fontSize': 10,
                                'fontWeight': 'normal',
                                'textOutline': False
                            }
                        }
                    }
                }
            },
        },
        'tooltip': {
            'borderWidth': 0,
            'borderRadius': 0,
            'shadow': False,
            'useHTML': True,
            'backgroundColor': "rgba(255,255,255,0)"  # make it transparent for hiding default background
        },
        'legend': {
            'useHTML': True
        },
        'plotOptions': {
            'pie': {
                'allowPointSelect': True,
                'dataLabels': {
                    'enabled': False,
                },

                'tooltip': {
                    'pointFormat': point_format if point_format else '{series.name}: {point.y}'
                },
                'showInLegend': True
            }
        },
    }


def get_stacked_column_chart_config(title, export_title, x_axis_title='', y_axis_title='', point_format=None, categories=list(),
                                    **kwargs):
    chart_config = {
        'chart': {
            'type': 'column'
        },
        'title': {
            'text': title,
            'useHTML': True
        },
        'exporting': {
            'sourceWidth': 900,
            'sourceHeight': 400,

            'chartOptions': {
                'title': {
                    'text': export_title
                },
                'plotOptions': {
                    'series': {
                        'dataLabels': {
                            'enabled': True,
                            'useHTML': True,
                            'format': '<span class="datalabel">{point.y:.0f}</span>',
                            'color': 'white',
                            'x': 3,
                            'y': 0,
                            'style': {
                                'fontSize': 9,
                                'fontWeight': 'normal',
                                'textOutline': False
                            }
                        }
                    }
                }
            }
        },
        'tooltip': {
            'borderWidth': 0,
            'borderRadius': 0,
            'shadow': False,
            'useHTML': True,
            'backgroundColor': "rgba(255,255,255,0)"  # make it transparent for hiding default background
        },
        'xAxis': {
            'categories': categories,
            'title': {
                'text': x_axis_title
            },
            'labels': {
                'useHTML': True
            },
        },
        'yAxis': {
            'title': {
                'text': y_axis_title
            }
        },
        'legend': {
            'useHTML': True
        },
        'plotOptions': {
            'column': {
                'stacking': True,
                'dataLabels': {
                    'enabled': False
                },
                'tooltip': {
                    'pointFormat': point_format if point_format else '{series.name}: {point.y:.0f}'
                },
            },
            'series': {
                'pointWidth': '40'
            }
        }
    }
    apply_params(chart_config, **kwargs)
    return chart_config


def get_column_chart_config(title, x_axis_title='', y_axis_title='', point_format=None, categories=list()):
    return {
        'chart': {
            'type': 'column'
        },
        'title': {
            'text': title,
            'useHTML': True
        },
        'exporting': {
            'sourceWidth': 900,
            'sourceHeight': 400,

            'chartOptions': {
                'plotOptions': {
                    'series': {
                        'dataLabels': {
                            'enabled': True,
                            'useHTML': True,
                            'format': '<span class="datalabel" >{point.y:.0f}</span>',
                            'color': 'rgb(102, 102, 102)',
                            'x': 3,
                            'y': 0,
                            'style': {
                                'fontSize': 9,
                                'fontWeight': 'normal',
                                'textOutline': False
                            }
                        }
                    }
                }
            }
        },

        'tooltip': {
            'borderWidth': 0,
            'borderRadius': 0,
            'shadow': False,
            'useHTML': True,
            'backgroundColor': "rgba(255,255,255,0)"  # make it transparent for hiding default background
        },
        'xAxis': {
            'categories': categories,
            'title': {
                'text': x_axis_title
            },
            'labels': {
                'useHTML': True
            },
        },
        'yAxis': {
            'title': {
                'text': y_axis_title
            }
        },
        'plotOptions': {
            'column': {
                'stacking': True,
                'tooltip': {
                    'pointFormat': point_format if point_format else '{series.name}: {point.y:.0f}'
                }
            },
            'series': {
                'pointWidth': '40'
            }
        },
        'legend': {
            'align': 'right',
            'x': 0,
            'y': 15,
            'verticalAlign': 'bottom',
            'floating': True,
            'borderColor': '#CCC',
            'borderWidth': 1,
            'shadow': False,
            'backgroundColor': 'white',
        }
    }


def get_stacked_bar_chart_config(
        title, export_title, x_axis_title='', y_axis_title='', point_format=None, categories=list(), **kwargs):
    chart_config = {
        'chart': {
            'type': 'bar'
        },
        'title': {
            'text': title,
            'useHTML': True
        },
        'exporting': {
            'sourceWidth': 900,
            'sourceHeight': 400,

            'chartOptions': {
                'title': {
                    'text': export_title
                },
                'plotOptions': {
                    'series': {
                        'dataLabels': {
                            'enabled': True,
                            'useHTML': True,
                            'format': '<span class="datalabel">{point.y:.0f}</span>',
                            'color': 'white',
                            'x': 3,
                            'y': 0,
                            'style': {
                                'fontSize': 9,
                                'fontWeight': 'normal',
                                'textOutline': False
                            }
                        }
                    }
                }
            }
        },
        'tooltip': {
            'borderWidth': 0,
            'borderRadius': 0,
            'shadow': False,
            'useHTML': True,
            'backgroundColor': "rgba(255,255,255,0)"  # make it transparent for hiding default background
        },
        'xAxis': {
            'categories': categories,
            'title': {
                'text': x_axis_title
            },
            'labels': {
                'useHTML': True
            },
        },
        'yAxis': {
            'title': {
                'text': y_axis_title
            }
        },
        'legend': {
            'useHTML': True
        },
        'plotOptions': {
            'bar': {
                'stacking': True,
                'dataLabels': {
                    'enabled': False
                },
                'tooltip': {
                    'pointFormat': point_format if point_format else '{series.name}: {point.y:.0f}'
                },
            },
            'series': {
                'pointWidth': '40'
            }
        }
    }
    apply_params(chart_config, **kwargs)
    return chart_config


def get_bar_chart_config(title, x_axis_title='', y_axis_title='', point_format=None, categories=list()):
    return {
        'chart': {
            'type': 'bar'
        },
        'title': {
            'text': title,
            'useHTML': True
        },
        'exporting': {
            'sourceWidth': 900,
            'sourceHeight': 400,

            'chartOptions': {
                'plotOptions': {
                    'series': {
                        'dataLabels': {
                            'enabled': True,
                            'useHTML': True,
                            'format': '<span class="datalabel" >{point.y:.0f}</span>',
                            'color': 'rgb(102, 102, 102)',
                            'inside': True,
                            'style': {
                                'fontSize': 9,
                                'fontWeight': 'normal',
                                'textOutline': False
                            }
                        }
                    }
                }
            }
        },
        'tooltip': {
            'borderWidth': 0,
            'borderRadius': 0,
            'shadow': False,
            'useHTML': True,
            'backgroundColor': "rgba(255,255,255,0)"  # make it transparent for hiding default background
        },
        'xAxis': {
            'categories': categories,
            'labels': {
                'useHTML': True
            },
            'title': {
                'text': x_axis_title,
            },
        },
        'yAxis': {
            'title': {
                'text': y_axis_title,
            },
        },
        'plotOptions': {
            'bar': {
                'dataLabels': {
                    'enabled': False
                },
                'tooltip': {
                    'pointFormat': point_format if point_format else '{series.name}: {point.y:.0f}'
                }
            }
        }
    }


def get_scatter_chart_config(title, x_axis_title='', y_axis_title='', decimal_places=2, categories=list()):
    return {
        'chart': {
            'type': 'scatter'
        },
        'title': {
            'text': title,
            'useHTML': True
        },

        'exporting': {
           'sourceWidth': 800,
           'sourceHeight': 400

        },
        'tooltip': {
            'borderWidth': 0,
            'borderRadius': 0,
            'shadow': False,
            'useHTML': True,
            'backgroundColor': "rgba(255,255,255,0)"  # make it transparent for hiding default background
        },
        'xAxis': {
            'title': {
                'enabled': True,
                'text': x_axis_title,
                'useHTML': True
            }
        },
        'yAxis': {
            'title': {
                'text': y_axis_title
            },
            'labels': {
                'format': '{value:.' + str(decimal_places) + 'f}'
            }
        },
        'plotOptions': {
            'scatter': {
                'tooltip': {
                    'pointFormat': x_axis_title + ': {point.x}<br/>' + y_axis_title + ': {point.y:.' + str(
                        decimal_places) + 'f}'
                }
            }
        }
    }
