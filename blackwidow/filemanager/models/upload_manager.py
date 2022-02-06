from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum

__author__ = 'Ziaul Haque'


@decorate(
    is_object_context,
    route(route='file-upload-manager', display_name='Upload Files',
          group='File Manager', module=ModuleEnum.DeviceManager, group_order=1, item_order=1)
)
class FileUploadManager(OrganizationDomainEntity):
    class Meta:
        app_label = 'filemanager'
