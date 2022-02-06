from blackwidow.core.models.roles.role import Role
from blackwidow.engine.decorators.utility import decorate, is_role_context

__author__ = 'Mahmud'


@decorate(is_role_context)
class Developer(Role):
    pass