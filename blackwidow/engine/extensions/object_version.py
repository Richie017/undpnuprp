from blackwidow.engine.enums.view_action_enum import ViewActionEnum


def get_object_if_version_requested(request=None, model=None, object=None):
    if request and object:
        try:
            return get_object_by_version(
                model=model,
                version_pk=int(
                    request.path_info.split(
                        ViewActionEnum.Version.value + '/'
                    )[1].split('/')[0]
                )
            )
        except Exception as e:
            return None
    return None


def get_object_by_version(model=None, version_pk=None):
    if model and version_pk:
        try:
            return model.all_objects.get(pk=version_pk)
        except:
            return None
    return None
