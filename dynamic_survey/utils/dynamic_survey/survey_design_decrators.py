"""This module is created for accommodating the functions that works with the decorator of a model which
can be used in the survey module. Currently there is only one function which updates the decorators of a model.
 """
from blackwidow.engine.decorators.utility import decorate
from blackwidow.core.models import ErrorLog


def update_model_decorator(model, *decorators):
    """
    This method updates the decorators of a model.

    :param model: the model we want to update the decorators
    :type model: django model object
    :param decorators: tuple of decorators used throughout any blackwidow project
    :type decorators: tuple
    :return: None
    :rtype: None
    """
    try:
        decorate(*decorators)(model)
    except Exception as e:
        ErrorLog.log(exp=e)
