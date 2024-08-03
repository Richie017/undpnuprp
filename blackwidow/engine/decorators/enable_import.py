__author__ = 'Mahmud'


def enable_import(original_class):
    importer_config = getattr(original_class, "importer_config", None)
    if not callable(importer_config):
        raise Exception(str(original_class) + " is decorated with 'enable_import' but does not implement 'importer_config(cls)'")

    import_item = getattr(original_class, "import_item", None)
    if not callable(import_item):
        raise Exception(str(original_class) + " is decorated with 'enable_import' but does not implement 'import_item(cls, data)'")
    return original_class