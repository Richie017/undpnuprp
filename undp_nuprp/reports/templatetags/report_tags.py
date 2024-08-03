from django import template

register = template.Library()


@register.filter(name='is_multiple_choice')
def is_multiple_choice(field):
    try:
        if field.field.widget.attrs['multiple'] == 'multiple':
            return True
    except:
        pass
    return False
