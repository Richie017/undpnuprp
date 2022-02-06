from blackwidow.core.forms.account.register import RegisterForm

__author__ = 'mahmudul'

from django.views.generic import *
from django.shortcuts import render


class RegisterView(FormView):
    template_name = "account/register.html"
    success_url = '/'
    form_class = RegisterForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            if form.verify_username(request) and form.verify_email(request) and form.verify_password(request):
                form.register(request)
                return super(RegisterView, self).form_valid(form)
        return super(RegisterView, self).form_invalid(form)


