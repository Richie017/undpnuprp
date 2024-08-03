__author__ = 'mahmudul'

import re

from django.core.management.base import BaseCommand

from settings import *


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.requires_model_validation = False

    def handle(self, *args, **options):
        _c = re.compile('(\s)*class(\s)+(?P<classname>(\w)+)\([a-zA-Z0-9_.]*(,(\s)*([a-zA-Z0-9_.])+)*\)')
        _n_c = re.compile('(\s)*class(\s)+Meta')
        patterns = list()
        for path in BW_INIT_INCLUDE_PATH:
            if path["destination"] not in patterns:
                patterns.append(path["destination"])
        for pattern in patterns:
            imports = list()
            all_classes = list()
            paths = [p for p in BW_INIT_INCLUDE_PATH if p["destination"] == pattern]
            _f = open(pattern, 'w')
            _f.write('')
            _f.close()
            for p in paths:
                for f in os.listdir(PROJECT_PATH + "/" + p["source"]):
                    if f.endswith(".py") and f != '__init__.py' and f[-4:] != '.pyc':
                        imports.append((p["source"] + "/" + f[:-3]).replace('/', '.'))
                        _path = p["source"] + '/' + f
                        with open(_path) as _file:
                            for line in _file:
                                result = _c.search(line)
                                if result is not None and _n_c.search(line) is None:
                                    all_classes.append(result.group('classname'))
                            _file.close()
            if len(imports) > 0:
                _f = open(pattern, 'w')
                _f.write('__author__ = "auto generated"\n\n')
                for _i in imports:
                    _f.write("from " + _i + " import * \n")
                _f.write('\n\n')
                i = 0
                for _i in all_classes:
                    if i == 0:
                        _f.write('__all__ = [\'' + _i + '\']\n')
                    else:
                        _f.write('__all__ += [\'' + _i + '\']\n')
                    i += 1
                _f.close()

            self.stdout.write(pattern + "   ...  generated")
