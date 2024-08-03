__author__ = 'mahmudul'

from django import forms
from django.contrib.auth import logout


class LogoutForm(forms.Form):

    def logout(self, request):
        logout(request)
        request.session.flush()
        return True


