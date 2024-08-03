from django import template

register = template.Library()


@register.filter(name='get_modules')
def get_modules(parent, modules):
    return modules.filter(parent_id=parent.pk).order_by('module_order')


@register.filter(name='get_menu_items')
def get_menu_items(module, menu_items):
    return menu_items.filter(group_name=module.name).order_by('item_order')
