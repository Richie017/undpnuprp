import operator

__author__ = 'ruddra'


def calculate_relational_operation(model_name, lhs, rhs, operators, self_comparison=False, counter_lhs=None):
    
    if not self_comparison:
        get_type = type(lhs).__name__
        if get_type == 'str':
            rhs = str(rhs)
        elif get_type == 'float':
            rhs = float(rhs)
        elif get_type == 'int':
            rhs = int(rhs)
    
        if operators == "==":
            if lhs == rhs:
                return True
            return False
        elif operators == "!=":
            if lhs != rhs:
                    return True
            return False
        elif operators == ">":
            if lhs > rhs:
                    return True
            return False
        elif operators == "<":
            if lhs < rhs:
                    return True
            return False
        elif operators == ">=":
            if lhs >= rhs:
                return True
            return False
        elif operators == "<=":
            if lhs == rhs:
                    return True
            return False
        elif operators == "Is":
            if lhs is rhs:
                return True
            return False
        return False
    else:
        if operators == "==":
            if lhs == counter_lhs:
                return True
            return False
        elif operators == "!=":
            if lhs != counter_lhs:
                return True
            return False
        elif operators == ">":
            if lhs > counter_lhs and operator.sub(lhs, counter_lhs) > rhs:
                return True
            return False
        elif operators == "<":
            if lhs < counter_lhs and operator.sub(rhs, counter_lhs) > rhs:
                return True
            return False
        elif operators == ">=":
            if lhs >= counter_lhs\
                    and operator.sub(rhs, counter_lhs) <= rhs:
                return True
            return False
        elif operators == "<=":
            if lhs <= counter_lhs and operator.sub(rhs, counter_lhs) <= rhs:
                return True
            return False
        elif operators == "Is":
            if lhs is counter_lhs:
                return True
            return False
        return False