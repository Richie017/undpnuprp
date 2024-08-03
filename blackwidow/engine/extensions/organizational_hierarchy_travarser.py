from blackwidow.core.models.log.error_log import ErrorLog

__author__ = 'Tareq'


def traverse_infrastructure_unit_hierarchy(h_list):
    try:
        last_elem = h_list[-1]
        if last_elem.parent_infrastructure_unit is None:
            return h_list
        return traverse_infrastructure_unit_hierarchy(h_list + [last_elem.parent_infrastructure_unit])
    except Exception as exp:
        ErrorLog.log(exp)
        return h_list
