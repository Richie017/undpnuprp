from blackwidow.core.models.contracts.configurabletype import ConfigurableType

from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate

__author__ = 'Ziaul Haque'


@decorate(route(route='document-tags'))
class DocumentTag(ConfigurableType):
    class Meta:
        app_label = 'filemanager'

    def to_json(self, depth=0, expand=None, wrappers=[], conditional_expand=[], **kwargs):
        obj = dict()
        obj['name'] = self.name
        return obj
