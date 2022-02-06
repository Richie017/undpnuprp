__author__ = 'Sohel'

import inspect

from blackwidow.core.signals.m2m_changed import TrackModelRelationChange


def enable_m2m_tracking(*filter_fields):  ##field names.
    def find_many_related_managers(original_class):
        members = inspect.getmembers(original_class)
        many_related_managers = {}
        for member in members:
            if "ReverseManyRelatedObjectsDescriptor" in str(type(member[1])):
                many_related_managers[member[0]] = member[1]
        return many_related_managers
    def enable_m2m_tracking_wrapper(original_class):
        many_related_managers = find_many_related_managers(original_class)
        if filter_fields:
            for filter_field in filter_fields:
                if filter_field in many_related_managers.keys():
                    TrackModelRelationChange.add_to_watch(many_related_managers[filter_field])
        else:
            for mm_name,mm_field in many_related_managers.items():
                TrackModelRelationChange.add_to_watch(mm_field)
        return original_class
    return enable_m2m_tracking_wrapper


