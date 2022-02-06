from blackwidow.core.models.email.email_template import EmailTemplate
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum

__author__ = 'ruddra'


@decorate(is_object_context,
          route(route='alert-email-template', display_name='Alert email template', module=ModuleEnum.Settings,
                group='Other Admin'))
class AlertEmailTemplate(EmailTemplate):
    class Meta:
        proxy = True
