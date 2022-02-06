__author__ = 'mahmudul'

from settings import *


def static(request):
    pathDictionary = dict()
    for i in STATICFILES_DIRS:
        pathDictionary[i['name'].upper() + '_URL'] = '/' + i['sub_site'] + 'content/' + i["name"].replace('_',
                                                                                                          '/') + '/'
    return pathDictionary