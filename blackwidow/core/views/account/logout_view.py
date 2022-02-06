__author__ = 'mahmudul'

from django.views.generic import *

from blackwidow.core.forms.account.logout_form import LogoutForm


class LogoutView(FormView):
    template_name = "account/login.html"
    success_url = '/account/login'
    form_class = LogoutForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        form.logout(request)
        return super(LogoutView, self).form_valid(form)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.logout(request)
            return super(LogoutView, self).form_valid(form)

        return super(LogoutView, self).form_invalid(form)


