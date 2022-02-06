from blackwidow.core.models.structure.infrastructure_unit import InfrastructureUnit

# @decorate(is_object_context,expose_api('warehouses'),
#           route(route='warehouses', module=ModuleEnum.Administration, group='Other Admin', display_name='Warehouse'))
class WareHouse(InfrastructureUnit):
    class Meta:
        proxy = True