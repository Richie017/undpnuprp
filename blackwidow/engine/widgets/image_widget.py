from django.forms import ClearableFileInput, CheckboxInput
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

__author__ = 'Ziaul Haque'


class ImageWidget(ClearableFileInput):
    """
        renders the input file as an thumbnail image, and modify the 'default html'
    """
    template_with_initial = u'%(initial)s %(clear_template)s<br />%(input)s'
    template_with_clear = '<div style="display:inline">%(clear)s ' \
                          '<label for="%(clear_checkbox_id)s">%(clear_checkbox_label)s</label></div>'

    def render(self, name, value, attrs=None):
        substitutions = {
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }
        template = u'%(input)s'
        _input = super(ClearableFileInput, self).render(name, value, attrs)
        _input_div = '<div class="custom-upload">' + _input +\
                     '<div class="fake-file"><input disabled="disabled" style="margin: 0 0 0 160px"></div></div>'
        substitutions['input'] = _input_div

        template = self.template_with_initial
        _url = '/static/img/dummy-photo.png'
        dummy_img_tag = '<img class="thumbnail-border" height="100" width="100" src="' + _url + '" />'
        substitutions['initial'] = (u'%s' % dummy_img_tag)

        if self.is_initial(value):
            substitutions['initial'] = (u'%s' % (value.instance.__str__()))
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                substitutions['clear'] = CheckboxInput().render(checkbox_name, False,
                                                                attrs={'id': checkbox_id, 'class': 'clear_image'})
                substitutions['clear_template'] = self.template_with_clear % substitutions

        return mark_safe(template % substitutions)

    def is_initial(self, value):
        return bool(value and hasattr(value, 'instance'))
