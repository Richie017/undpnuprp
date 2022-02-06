import collections

from blackwidow.engine.encoders.bw_json_encoder import DynamicJsonEncoder


__author__ = 'mahmudul'

from django import http


class JsonMixin(object):
    # def get_success_url(self):
    # return '/' + settings.SUB_SITE + self.success_url

    def is_json_request(self, request):
        if request.GET.get('format', 'html') == 'json' \
                or request.POST.get('format', 'html') == 'json':
            return True
        return False

    def build_json_message(self, message, errors, success, kwargs={}):
        if 'authkey' in kwargs:
            return {
                'message': message,
                'errors': errors,
                "success": success,
                'authkey': kwargs['authkey']
            }
        return {
            'message': message,
            'errors': errors,
            "success": success
        }

    def extract_parameter(self, pname):
        return self.request.GET.get(pname, None) or self.request.POST.get(pname, None)

    def render_json_response(self, context):
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **kwargs):
        return http.HttpResponse(content,
                                 content_type='application/json',
                                 **kwargs)

    def json_serialize_array(self, data, **kwargs):
        if isinstance(data, collections.Iterable):
            ndata = []
            for d in data:
                ndata.append(d.to_json(**kwargs))
            return ndata
        else:
            return data.to_json(**kwargs)

    def json_serialize_object(self, data, **kwargs):
        return data.to_json(**kwargs)

    def convert_context_to_json(self, context):
        encoder = DynamicJsonEncoder()
        return encoder.encode(context)
