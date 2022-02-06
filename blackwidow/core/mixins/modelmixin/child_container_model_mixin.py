__author__ = 'Mahmud'


class ChildContainerModelMixin(object):
    def remove_m2m(self, items, *args, **kwargs):
        for x in items.all():
            items.remove(x)
            x.delete(*args, **kwargs)

    def add_child_item(self, **kwargs):
        tab = [x for x in self.tabs_config if x.access_key == kwargs['tab']][0]
        for _id in kwargs['ids'].split(','):
            tab.add_item(tab.get_model().objects.get(pk=int(_id)))

    def remove_child_item(self, **kwargs):
        tab = [x for x in self.tabs_config if x.access_key == kwargs['tab']][0]
        for _id in kwargs['ids'].split(','):
            tab.remove_item(tab.get_model().objects.get(pk=int(_id)))
            if tab.access_key in self.__class__.get_dependent_field_list():
                tab.get_model().objects.get(pk=int(_id)).delete()



