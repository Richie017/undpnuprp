from abc import abstractmethod

__author__ = 'Mahmud'


class ModelFactory(object):

    @abstractmethod
    def generate_model(self, data=None, **kwargs):
        return None

    @abstractmethod
    def generate_storage(self, model=None):
        return None

