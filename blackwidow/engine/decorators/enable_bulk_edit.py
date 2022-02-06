

def enable_bulk_edit(row_pivots=[], column_pivots=[], fallback_default=True):
    registry = {}
    kwargs = {
        'row_pivots': row_pivots,
        'column_pivots': column_pivots,
        'fallback_default': fallback_default
    }

    def enable_bulk_edit(original_class):
        if '_registry' in dir(original_class):
            if original_class.__name__ not in original_class._registry:
                original_class._registry[original_class.__name__] = dict()

            if 'enable_bulk_edit' in original_class._registry[original_class.__name__]:
                original_class._registry[original_class.__name__]['enable_bulk_edit'].update(**kwargs)
            else:
                original_class._registry[original_class.__name__]['enable_bulk_edit'] = dict(**kwargs)
        else:
            registry[original_class.__name__] = dict()
            registry[original_class.__name__]['enable_bulk_edit'] = dict(**kwargs)
            original_class._registry = registry
        return original_class
    return enable_bulk_edit
