from blackwidow.core.generics.views.partial_views.partial_create_view import PartialGenericCreateView
from blackwidow.filemanager.models.uploadfileobject import UploadFileObject

__author__ = 'Ziaul Haque'


class PartialFileUploadView(PartialGenericCreateView):

    def post(self, request, *args, **kwargs):
        if self.form_class.Meta.model.__name__ == UploadFileObject.__name__:
            parent_id = kwargs['parent_id']
            model = self.model.objects.filter(id=int(parent_id))[0]
            if self.request.POST.get('ids', '') != '':
                model.add_child_item(
                    ids=self.request.POST.get('ids', ''), user=self.request.c_user,
                    organization=self.request.c_organization, **kwargs)
            return self.render_json_response(dict(
                message="Items added successfully.",
                success=True,
                load="ajax",
                load_tabs=False
            ))
        return super(PartialFileUploadView, self).post(request, *args, **kwargs)
