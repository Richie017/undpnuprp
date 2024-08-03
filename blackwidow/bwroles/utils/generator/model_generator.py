import os

from blackwidow.bwroles.utils.generator.code_generator import BWCodeGenerator
from blackwidow.engine.extensions.bw_titleize import bw_titleize

__author__ = 'Sohel, Tareq'


class BWModelGenerator(BWCodeGenerator):

    @classmethod
    def get_model_path(cls, module_name):
        path = str(module_name) + '.models.users.base'
        path = path.replace('.', os.sep)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @classmethod
    def get_model_customization_path(cls, module_name):
        path = str(module_name) + '.models.users.customization'
        path = path.replace('.', os.sep)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @classmethod
    def generate_modelmixin_import_path(cls, path, mixin_file_name, model_name):
        import_path = 'from ' + path.replace(os.sep, '.') + '.' + mixin_file_name.lower() + ' import ' + model_name+"ModelBase"
        return import_path

    @classmethod
    def generate_model(cls, model_name, app_label=None, parent_model='DomainEntity', imports=[], route_name=None,
                       module_name='Administration', group_name='Others', display_name=None, api_expose=False,
                       table_columns=[], details_buttons=[], is_role_context=False, is_object_context=False,
                       is_business_role=False, save_audit_log=False, inline_manage_button=[], proxy=False, **kwargs):

        route_name = route_name if route_name is not None else model_name.lower()
        display_name = display_name if display_name is not None else bw_titleize(model_name)
        decorators = list()
        if is_role_context:
            imports.append('from blackwidow.engine.decorators.utility import is_role_context')
            decorators.append('is_role_context')
        if is_object_context:
            imports.append('from blackwidow.engine.decorators.utility import is_object_context')
            decorators.append('is_object_context')
        if save_audit_log:
            imports.append('from blackwidow.engine.decorators.utility import save_audit_log')
            decorators.append('save_audit_log')
        if is_business_role:
            imports.append('from blackwidow.engine.decorators.route_partial_routes import is_business_role')
            decorators.append('is_business_role')
        if display_name and group_name:
            imports.append('from blackwidow.engine.decorators.route_partial_routes import route')
            imports.append('from blackwidow.engine.enums.modules_enum import ModuleEnum')
            decorators.append('route(route="%s", group="%s", module=ModuleEnum.%s,display_name="%s")' % (
                route_name, group_name, module_name, display_name))
        if api_expose:
            imports.append('from blackwidow.engine.decorators.expose_model import expose_api')
            decorators.append('expose_api("%s")' % route_name)


        model_customization_path = cls.get_model_customization_path(module_name=app_label)
        model_mixin_file_name = model_name.lower()+"_modelbase"

        model_mixin_import_path = cls.generate_modelmixin_import_path(model_customization_path, model_mixin_file_name, model_name)

        imports += [ model_mixin_import_path ]

        model_mixin_source_code, model_class_source_code = cls.generate_python_model_class(model_name, parent_model, imports=imports,
                                                            decorators=decorators, proxy=proxy)

        model_mixin_file_name += ".py"

        file_path = os.path.join(model_customization_path, model_mixin_file_name)
        if not os.path.isfile(file_path):
            cls.generate_source_file(model_customization_path, model_mixin_file_name, model_mixin_source_code)

        model_path = cls.get_model_path(module_name=app_label)
        file_name = model_name.lower() + ".py"
        cls.generate_source_file(model_path, file_name, model_class_source_code)
        return model_path, file_name
