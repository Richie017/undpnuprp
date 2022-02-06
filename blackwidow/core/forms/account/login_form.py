__author__ = 'mahmudul'

from django import forms
from django.contrib.auth import authenticate, login
# from django.contrib.auth.hashers import make_password, check_password


class LoginForm(forms.Form):
    username = forms.CharField(required=True, label="Username")
    password = forms.CharField(required=True, widget=forms.PasswordInput)
    timezone = forms.CharField(required=False, widget=forms.HiddenInput)
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput, label="Remember Me?")

    def authenticate(self, request):

        # hashed_pwd = make_password("123456")
        # self.add_error(None,hashed_pwd)
        # return False
        data = self.cleaned_data
        user = authenticate(username=data["username"], password=data["password"])
        print(user)
        if user is not None:
            if user.is_active:
                login(request, user)
                request.session.set_expiry(86400)
                return True
            else:
                self.add_error(None, "Your account has been disabled!")
        else:
            self.add_error(None, "Your username and password were incorrect.")
        return False



