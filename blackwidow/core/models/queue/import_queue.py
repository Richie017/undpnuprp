from blackwidow.core.models.queue.queue import FileQueue
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum

__author__ = 'Mahmud'


@decorate(is_object_context,
          route(route='import-queues', group='Import/Export', module=ModuleEnum.Settings,
                display_name="Import Queue"))
class ImportFileQueue(FileQueue):
    class Meta:
        proxy = True
