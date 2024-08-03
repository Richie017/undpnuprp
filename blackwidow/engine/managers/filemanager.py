import os

__author__ = 'Mahmud'


class FileManager(object):
    @classmethod
    def create_dirs(cls, path):
        if not os.path.exists(path):
            os.makedirs(path)

    @classmethod
    def delete_dirs(cls, path):
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

    @classmethod
    def delete_file(cls, path):
        os.remove(path)