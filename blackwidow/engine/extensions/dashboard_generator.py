from blackwidow.engine.decorators.utility import get_models_with_decorator
from blackwidow.engine.enums.modules_enum import ModuleEnum
from config.apps import INSTALLED_APPS

__author__ = 'Imtiaz'


def dashboard_generator(module=None):
    all_models = get_models_with_decorator('route', INSTALLED_APPS, include_class=True)
    all_models = [x for x in all_models if not bool(x.get_model_meta('route', 'hide'))]

    modules = [ModuleEnum.Reports, ModuleEnum.Alert, ModuleEnum.Targets, ModuleEnum.Execute, ModuleEnum.Administration,
               ModuleEnum.Survey, ModuleEnum.Settings]

    for _m in modules:
        if _m.value['route'] == module:
            return [x for x in all_models if
                    x.get_model_meta('route', 'module') is not None and x.get_model_meta('route', 'module').value[
                        'route'] == module]
    return []
