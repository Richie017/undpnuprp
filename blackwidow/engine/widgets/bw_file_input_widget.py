from django.conf import settings
from django.forms.widgets import ClearableFileInput
from django.utils.html import conditional_escape

STATIC_UPLOAD_URL = settings.STATIC_UPLOAD_URL

__author__ = 'Shuvro'


class BWFileInput(ClearableFileInput):
    # change initial template so that in edit form there will be a button to download existing file

    template_with_initial = (
        '%(initial_text)s: <a title="%(initial)s" target="_blank" href="%(initial_url)s" >'
        '<i class="fa fa-download" aria-hidden="true"></i></a> '
        '%(clear_template)s<br />%(input_text)s: %(input)s'
    )

    def get_template_substitution_values(self, value):
        '''
        :param value:
        :return: a dict where 'initial' refers to the name of the uploaded file and
        'initial_url' refers the url of the uploaded file which is used to download
        '''
        try:
            _file_name = value.name.split('/')[-1]
            _initial_url = STATIC_UPLOAD_URL + _file_name
        except:
            _file_name = ''
            _initial_url = ''

        return {
            'initial': conditional_escape(_file_name),
            'initial_url': conditional_escape(_initial_url),
        }
