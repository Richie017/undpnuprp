from blackwidow.bwroles.models.users.base.admin import Admin
from blackwidow.bwroles.forms.users.customization.admin_baseform import AdminBaseForm

__author__='__auto_generated__'


class AdminForm(AdminBaseForm):
    class Meta(AdminBaseForm.Meta):
        model = Admin
