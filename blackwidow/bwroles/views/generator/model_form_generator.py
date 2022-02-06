import os

from django.conf import settings
from django.http.response import JsonResponse

from blackwidow.bwroles.models.generator.model_form_generator import ModelFormGenerator
from blackwidow.bwroles.utils.generator.form_generator import BWFormGenarator
from blackwidow.bwroles.utils.generator.model_generator import BWModelGenerator
from blackwidow.core.generics.views.list_view import GenericListView
from blackwidow.core.models.roles.role import Role
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum

__author__ = 'Sohel'
__organization__ = 'FIS'


@decorate(override_view(model=ModelFormGenerator, view=ViewActionEnum.Manage))
class ModelFormGeneratorView(GenericListView):
    def get_template_names(self):
        return ['generator/model_form_generator.html']

    def handle_model_generation(self, model_name, app_label):
        imports = [
            'from blackwidow.core.models import ConsoleUser'
        ]

        params = dict()
        params['model_name'] = model_name.replace(' ', '')
        params['app_label'] = app_label
        params['parent_model'] = 'ConsoleUser'
        params['imports'] = imports
        params['group_name'] = 'Users'
        params['proxy'] = True
        params['is_role_context'] = True
        params['is_object_context'] = True
        params['save_audit_log'] = True
        params['api_expose'] = True

        return BWModelGenerator.generate_model(**params)

    def handle_form_generation(self, form_name, app_label, associated_model, model_path):
        associated_model = associated_model.replace(' ', '')
        imports = [
            'from blackwidow.bwroles.forms.users.user_form import GenericUserForm',
            'from ' + model_path.replace(os.sep, '.') + '.' + associated_model.lower() + ' import ' + associated_model
        ]
        return BWFormGenarator.generate_form(form_name, 'GenericUserForm', associated_model, app_label, imports)

    def get(self, request, *args, **kwargs):
        try:
            if request.GET.get('action', 'false') == 'true':
                model_name = request.GET.get('model_name')
                if model_name is not None:
                    model_path, model_file = self.handle_model_generation(model_name, settings.ROLES_APP)
                    self.handle_form_generation(model_name.replace(' ', '') + 'Form', settings.ROLES_APP, model_name,
                                                model_path)
                    return JsonResponse({
                        'success': True
                    })

            else:
                return super().get(request, *args, **kwargs)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': e
            })

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        all_roles = Role.objects.exclude(name__in=['Developer', 'SystemAdmin']).order_by('name')
        roles_models = []
        for role_model in all_roles:
            roles_models.append({
                'role_name': role_model.name
            })
        context_data['roles_models'] = roles_models
        return context_data
