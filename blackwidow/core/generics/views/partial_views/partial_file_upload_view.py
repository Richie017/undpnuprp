from blackwidow.core.generics.views.partial_views.partial_create_view import PartialGenericCreateView
from blackwidow.filemanager.models.uploadfileobject import UploadFileObject

__author__ = 'Ziaul Haque'


class PartialGenericFileUploadView(PartialGenericCreateView):

    def get_template_names(self):
        if self.form_class.Meta.model.__name__ == UploadFileObject.__name__:
            return ['_file_upload_partial.html']
        return super(PartialGenericFileUploadView, self).get_template_names()

    def get_context_data(self, **kwargs):
        context = super(PartialGenericFileUploadView, self).get_context_data(**kwargs)
        context['language_code'] = self.request.LANGUAGE_CODE
        return context

    def post(self, request, *args, **kwargs):
        if self.form_class.Meta.model.__name__ == UploadFileObject.__name__:
            id = kwargs['parent_id']
            model = self.model.objects.filter(id=int(id))[0]
            if self.request.POST.get('ids', '') != '':
                model.add_child_item(
                    ids=self.request.POST.get('ids', ''),
                    user=self.request.c_user,
                    organization=self.request.c_organization,
                    **kwargs
                )

                model.app_assignment(
                    ids=self.request.POST.get('ids', ''),
                    path=self.request.path,
                    **kwargs
                )

            return self.render_json_response(dict(
                message="Items added successfully.",
                success=True,
                load="ajax",
                load_tabs=False
            ))
        return super(PartialGenericFileUploadView, self).post(request, *args, **kwargs)
