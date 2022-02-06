import os

from blackwidow.bwroles.utils.generator.code_generator import BWCodeGenerator

__author__ = 'Sohel, Tareq'

class BWFormGenarator(BWCodeGenerator):
    @classmethod
    def get_form_path(cls, module_name):
        path = str(module_name) + '.forms.users.base'
        path = path.replace('.', os.sep)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @classmethod
    def get_form_customization_path(cls, module_name):
        path = str(module_name) + '.forms.users.customization'
        path = path.replace('.', os.sep)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @classmethod
    def generate_formmixin_import_path(cls, path, mixin_file_name, model_name):
        import_path = 'from ' + path.replace(os.sep, '.') + '.' + mixin_file_name.lower() + ' import ' + model_name+"BaseForm"
        return import_path

    @classmethod
    def generate_form(cls, form_class_name, base_class_name, model_name, app_label, imports=[], **kwargs):

        form_customization_path = cls.get_form_customization_path(module_name=app_label)
        form_mixin_file_name = model_name.lower()+"_baseform"

        form_mixin_import_path = cls.generate_formmixin_import_path(form_customization_path, form_mixin_file_name, model_name)

        imports += [ form_mixin_import_path ]

        mixin_source_code, form_source_code = BWCodeGenerator.generate_python_form_class(form_class_name, base_class_name, model_name,
                                                                      imports=imports)

        form_mixin_file_name += ".py"

        file_path = os.path.join(form_customization_path, form_mixin_file_name)
        if not os.path.isfile(file_path):
            cls.generate_source_file(form_customization_path, form_mixin_file_name, mixin_source_code)

        form_path = cls.get_form_path(module_name=app_label)
        file_name = form_class_name.lower() + ".py"
        cls.generate_source_file(form_path, file_name, form_source_code)
        return form_path, file_name
