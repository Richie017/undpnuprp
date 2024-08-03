from django.contrib import messages
from django.shortcuts import redirect

from blackwidow.core.generics.views.create_view import GenericCreateView

__author__ = 'Mahmud'


class PartialGenericDeleteView(GenericCreateView):
    form_kwargs = None

    def get(self, request, *args, **kwargs):
        self.form_kwargs = kwargs
        form = self.get_form(self.get_form_class())
        try:
            if 'tab' in kwargs:
                id = kwargs['parent_id']
                model = self.model.objects.filter(id=int(id))[0]
                model.remove_child_item(ids=self.request.GET.get('ids', ''), user=self.request.c_user,
                                        organization=self.request.c_organization, **kwargs)

        except Exception as err:
            messages.error(request, str(err))
            return self.form_invalid(form)
        return self.form_valid(form)

    def form_valid(self, form):
        if self.is_json_request(self.request) or self.request.is_ajax():
            return self.render_json_response({
                'success': True,
                'message': 'Operation completed successfully.',
                'load': 'ajax',
            })
        return redirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.form_kwargs:
            kwargs.update(self.form_kwargs)
        return kwargs