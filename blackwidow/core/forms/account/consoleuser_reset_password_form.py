from datetime import datetime
from threading import Thread

from django.contrib.sessions.models import Session
from rest_framework.authtoken.models import Token

from blackwidow.core.mixins.formmixin.form_mixin import GenericDefaultFormMixin
from blackwidow.core.models.log.error_log import ErrorLog

__author__ = 'ruddra, Tareq'
from django import forms


class ConsoleUserResetPasswordForm(GenericDefaultFormMixin):
    password = forms.CharField(widget=forms.PasswordInput)
    retype_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data['password']
        re_password = cleaned_data['retype_password']
        if password != re_password:
            self.add_error('password', "passwords don't match")
        return cleaned_data

    def delete_all_unexpired_session_for_user(self, user):
        try:
            deletable_session_ids = list()
            for session in Session.objects.filter(expire_date__gte=datetime.now()):
                if session.get_decoded()['context']['user']['id'] == user.pk:
                    deletable_session_ids.append(session.pk)
            Session.objects.filter(pk__in=deletable_session_ids).delete()
        except Exception as exp:
            ErrorLog.log(exp=exp)

    def save(self, **kwargs):
        password = self.cleaned_data['password']
        user = kwargs['user']
        user.set_password(password)
        user.save()

        # Delete Tokens for user, so that user is forced to login again from mobile.
        Token.objects.filter(user_id=user.pk).delete()

        # Clear sessions for user, so that user is forced to login again from Mission Control
        # As clearing session is time consuming process, we do it in seperate thread
        session_clear_process = Thread(target=self.delete_all_unexpired_session_for_user, args=(user,))
        session_clear_process.start()
