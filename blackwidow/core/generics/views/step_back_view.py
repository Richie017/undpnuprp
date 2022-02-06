from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.base import TemplateView

from blackwidow.core.mixins.viewmixin.protected_view_mixin import ProtectedViewMixin

__author__ = 'Sohel'

class GenericStepBackView(ProtectedViewMixin, TemplateView):

    def process_request(self,request,request_method,*args,**kwargs):
        models = None
        if kwargs.get('ids', '') != '':
            models = self.model.objects.filter(id__in=kwargs.get('ids').split(','))

        reqeust_data_array = request.GET
        if request_method == "POST":
            reqeust_data_array = request.POST
        if reqeust_data_array.get('ids', '') != '':
            models = self.model.objects.filter(id__in=kwargs.get('ids').split(','))

        if not models:
            if self.is_json_request(request) or request.is_ajax():
                return self.render_json_response({
                    'message':  'Nothing to step back.',
                    'success': False,
                    'load': 'ajax'
                })
            messages.warning(request, 'Nothing to step back.')
            return redirect(self.get_success_url())


        for m in models:
            m = m.execute_step_back(user=request.c_user,data = reqeust_data_array)

        if self.is_json_request(request) or request.is_ajax():
            return self.render_json_response({
                'message':  'Request completed successfully.',
                'success': True,
                'load': 'ajax',
                'success_url': self.model.success_url() if hasattr(self.model, 'success_url') else None,
            })
        return redirect(self.get_success_url())

    def get(self, request, *args, **kwargs):
        return self.process_request(request,"GET",*args,**kwargs)

    def post(self, request, *args, **kwargs):
        return self.process_request(request,"POST",*args,**kwargs)
