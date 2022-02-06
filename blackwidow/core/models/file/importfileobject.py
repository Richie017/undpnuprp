from blackwidow.core.models.file.fileobject import FileObject
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum

__author__ = 'ruddra'


@decorate(is_object_context,
          route(route='import-files', group='Import/Export', module=ModuleEnum.Settings, display_name="Data File"))
class ImportFileObject(FileObject):
    class Meta:
        proxy = True

    @classmethod
    def all(cls):
        return FileObject.objects.filter(file_type=cls.__name__)
