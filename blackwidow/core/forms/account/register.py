from blackwidow.core.managers.contextmanager import ContextManager

__author__ = 'mahmudul'

import re

from django import forms
from django.contrib.auth.admin import User

from blackwidow.core.models.users.web_user import WebUser


class RegisterForm(forms.Form):
    username = forms.CharField(label="Username")
    email = forms.EmailField(label="Email", widget=forms.EmailInput)
    confirm_email = forms.EmailField(label="Confirm Email", widget=forms.EmailInput)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    def verify_username(self, request):
        data = self.cleaned_data
        if len(data["username"]) < 6:
            msg = u"Username must contain at least 6 characters."
            self._errors["username"] = self.error_class([msg])
            return False
        if not re.search('[a-z|A-Z]', data["username"]):
            msg = u"Username must contain some letters."
            self._errors["username"] = self.error_class([msg])
            return False
        if User.objects.filter(username=data["username"]).count() > 0:
            msg = u"Username already exists."
            self._errors["username"] = self.error_class([msg])
            return False
        return True

    def verify_password(self, request):
        data = self.cleaned_data
        if len(data["password"]) < 6:
            msg = u"Password must contain at least 6 characters."
            self._errors["confirm_password"] = self.error_class([msg])
            return False
        if re.search('[a-z|A-Z]', data["password"]) and re.search(r'[0-9]', data["password"]):
            if data["password"] != data["confirm_password"]:
                msg = u"Password and Confirm Password must match."
                self._errors["confirm_password"] = self.error_class([msg])
        else:
            msg = u"Password must contain at a number and a  letter."
            self._errors["confirm_password"] = self.error_class([msg])
            return False
        return data["password"] == data["confirm_password"]

    def verify_email(self, request):
        data = self.cleaned_data
        if data["email"] != data["confirm_email"]:
            msg = u"Email and Confirm Email must match."
            self._errors["confirm_email"] = self.error_class([msg])
        return data["email"] == data["confirm_email"]

    def register(self, request):
        data = self.cleaned_data
        try:
            if User.objects.filter(username=data["username"]).count() == 0:
                new_user = User(username=data["username"])
                new_user.set_password(data["password"])
                new_user.email = data["email"]
                new_user.save(request=request, context=ContextManager.get_current_context(request))
                web_user = WebUser()
                web_user.user = User.objects.get(id=new_user.id)
                web_user.save(request=request, context=ContextManager.get_current_context(request))
                return True
        except Exception as e:
            print(e)
            return False

    def clean_username(self):
        data = self.cleaned_data
        if len(data["username"]) < 6:
            msg = u"Username must contain at least 6 characters."
            self._errors["username"] = self.error_class([msg])
            return False
        if not re.search('[a-z|A-Z]', data["username"]):
            msg = u"Username must contain some letters."
            self._errors["username"] = self.error_class([msg])
            return False
        if User.objects.filter(username=data["username"]).count() > 0:
            msg = u"Username already exists."
            self._errors["username"] = self.error_class([msg])
            return False
        return True

    def clean_password(self):
        data = self.cleaned_data
        if len(data["password"]) < 6:
            msg = u"Password must contain at least 6 characters."
            self._errors["confirm_password"] = self.error_class([msg])
            return False
        if re.search('[a-z|A-Z]', data["password"]) and re.search(r'[0-9]', data["password"]):
            if data["password"] != data["confirm_password"]:
                msg = u"Password and Confirm Password must match."
                self._errors["confirm_password"] = self.error_class([msg])
        else:
            msg = u"Password must contain at a number and a  letter."
            self._errors["confirm_password"] = self.error_class([msg])
            return False
        return data["password"] == data["confirm_password"]

    def clean_email(self):
        data = self.cleaned_data
        if data["email"] != data["confirm_email"]:
            msg = u"Email and Confirm Email must match."
            self._errors["confirm_email"] = self.error_class([msg])
        return data["email"] == data["confirm_email"]
