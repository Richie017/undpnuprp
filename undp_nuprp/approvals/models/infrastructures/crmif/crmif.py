from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.approvals.models.infrastructures.base.base_settlement_infrastructure_fund import \
    BaseSettlementInfrastructureFund

__author__ = 'Shuvro'


@decorate(is_object_context,
          route(route='crmif', group='Infrastructure & Urban Services',
                module=ModuleEnum.Analysis,
                display_name='CRMIF', group_order=5, item_order=1))
class CRMIF(BaseSettlementInfrastructureFund):

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Create, ViewActionEnum.Edit, ViewActionEnum.AdvancedExport]

    @classmethod
    def get_object_inline_buttons(cls):
        return [ViewActionEnum.Details, ViewActionEnum.Edit]

    @classmethod
    def get_button_title(cls, button=ViewActionEnum.Details):
        if button == ViewActionEnum.AdvancedExport:
            return "Export"
        elif button == ViewActionEnum.AdvancedImport:
            return "Import"

    class Meta:
        app_label = 'approvals'
