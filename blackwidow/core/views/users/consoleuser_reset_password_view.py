from django.contrib import messages
from django.views.generic.edit import FormView

from blackwidow.core.forms.account.consoleuser_reset_password_form import ConsoleUserResetPasswordForm
from blackwidow.core.mixins.viewmixin.protected_view_mixin import ProtectedViewMixin
from blackwidow.core.models.log.error_log import ErrorLog
from blackwidow.core.models.users.user import ConsoleUser

__author__ = 'ruddra'


class ConsoleUserResetPasswordView(ProtectedViewMixin, FormView):
    form_class = ConsoleUserResetPasswordForm
    success_url = '/'
    template_name = 'shared/display-templates/_partial_generic_form.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            id = kwargs['id']
            try:
                form.save(user=ConsoleUser.objects.get(pk=id).user)
                messages.success(request, 'Password has been reset.')
            except Exception as exp:
                messages.error(request, exp)
                ErrorLog.log(exp)
                return self.form_invalid(form)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
