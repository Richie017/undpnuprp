from blackwidow.bwroles.forms.users.user_form import GenericUserForm

__author__='__auto_generated__'


class AdminBaseForm(GenericUserForm):
    def __init__(self, data=None, files=None, instance=None, allow_login=True, **kwargs):
        super().__init__(data=data, files=files, instance=instance, **kwargs)
