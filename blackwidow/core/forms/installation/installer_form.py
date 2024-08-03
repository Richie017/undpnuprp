from django import forms

from blackwidow.core.managers.contextmanager import ContextManager
from blackwidow.core.models.organizations.organization import Organization


__author__ = 'mahmudul'


class InstallerForm(forms.Form):
    organization_name = forms.CharField(required=True, label="Organization Name")
    superadmin_name = forms.CharField(required=True, label="Full Name")
    superadmin_username = forms.CharField(required=True, label="Login Name")
    superadmin_email = forms.CharField(required=True, label="Email")
    superadmin_confirmemail = forms.CharField(required=True, label="Confirm Email")
    superadmin_password = forms.CharField(required=True, label="Password")
    superadmin_confirmpassword = forms.CharField(required=True, label="Confirm Password")

    #initialize the system with startup company and users
    def initialize_system(self, request):
        data = self.cleaned_data

        #initialize the company
        org = Organization()
        org.name = data['organization_name']
        org.save(request=request, context=ContextManager.get_current_context(request))


        #initialize the super user
        #initilaize the administrators
        pass