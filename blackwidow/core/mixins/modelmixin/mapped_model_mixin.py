from config.apps import INSTALLED_APPS as apps

__author__ = 'Mahmud, Tareq'


class MappedModelMixin(object):
    @property
    def map_data(self):
        return ''

    @property
    def has_map(self):
        return False

    def app_full_label(self, dir_format=False):
        label = self._meta.app_label
        for app in apps:
            if app.split('.')[-1] == label:
                label = app
                break
        if dir_format:
            label = label.replace('.', '/')
        return label
