__author__ = 'ruddra'


def enable_export(original_class):
    importer_config = getattr(original_class, "exporter_config", None)
    if not callable(importer_config):
        raise Exception(str(original_class) + " is decorated with 'exporter_config' but does not implement 'export_config(cls)'")

    export_item = getattr(original_class, "export_item", None)
    if not callable(export_item):
        raise Exception(str(original_class) + " is decorated with 'enable_export' but does not implement 'export_item(cls, data)'")

    finalize_export = getattr(original_class, "finalize_export", None)
    if not callable(finalize_export):
        raise Exception(str(original_class) + " is decorated with 'enable_export' but does not implement 'finalize_export(cls, data)'")

    initialize_export = getattr(original_class, "initialize_export", None)
    if not callable(initialize_export):
        raise Exception(str(original_class) + " is decorated with 'enable_export' but does not implement 'initialize_export(cls, data)'")

    return original_class