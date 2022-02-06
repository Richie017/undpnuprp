from blackwidow.engine.enums.view_action_enum import ViewActionEnum

__author__ = 'Tareq'


def deactivatable_model(original_class):
    # Getting original class manage buttons
    manage_buttons = original_class.get_manage_buttons()
    if ViewActionEnum.Deactivate not in manage_buttons:
        manage_buttons += [ViewActionEnum.Deactivate]

    # Getting original class object inline buttons
    object_inline_buttons = original_class.get_object_inline_buttons()
    if ViewActionEnum.Delete in object_inline_buttons:
        object_inline_buttons.remove(ViewActionEnum.Delete)
    if ViewActionEnum.Deactivate not in object_inline_buttons:
        object_inline_buttons += [ViewActionEnum.Deactivate]

    # Defining new method to override original class's get_manage_buttons()
    def new_manage_buttons():
        return manage_buttons

    # Defining new method to override original class's get_object_inline_buttons()
    def new_inline_buttons():
        return object_inline_buttons

    original_class.get_manage_buttons = new_manage_buttons
    original_class.get_object_inline_buttons = new_inline_buttons

    return original_class


def reactivatable_model(original_class):
    # Getting original class manage buttons
    manage_buttons = original_class.get_manage_buttons()
    if ViewActionEnum.Activate not in manage_buttons:
        manage_buttons += [ViewActionEnum.Activate]

    # Getting original class object inline buttons
    object_inline_buttons = original_class.get_object_inline_buttons()
    if ViewActionEnum.Delete in object_inline_buttons:
        object_inline_buttons.remove(ViewActionEnum.Delete)
    if ViewActionEnum.Activate not in object_inline_buttons:
        object_inline_buttons += [ViewActionEnum.Activate]

    # Defining new method to override original class's get_manage_buttons()
    def new_manage_buttons():
        return manage_buttons

    # Defining new method to override original class's get_object_inline_buttons()
    def new_inline_buttons():
        return object_inline_buttons

    original_class.get_manage_buttons = new_manage_buttons
    original_class.get_object_inline_buttons = new_inline_buttons

    return original_class
