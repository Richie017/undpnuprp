from blackwidow.dbmediabackup.utils.storages.dropbox_storage.dropbox_base import DropBoxStorage

__author__ = "Ziaul Haque"


def _size_in_byte(file_content):
    """
    Get file's size to byte.

    :param file_content: File to handle
    :type file_content: file

    :returns: File's size in bytes
    :rtype: integer
    """
    file_content.seek(0, 2)
    _size = file_content.tell()
    file_content.seek(0)
    return _size


class BWDropBoxStorage(DropBoxStorage):
    def __init__(self, oauth2_access_token=None, root_path=None):
        super(BWDropBoxStorage, self).__init__(oauth2_access_token, root_path)

    def _full_path(self, name):
        return super(BWDropBoxStorage, self)._full_path(name)

    def delete(self, name):
        super(BWDropBoxStorage, self).delete(name)

    def exists(self, name):
        return super(BWDropBoxStorage, self).exists(name)

    def listdir(self, path):
        return super(BWDropBoxStorage, self).listdir(path)

    def size(self, name):
        return super(BWDropBoxStorage, self).size(name)

    def modified_time(self, name):
        return super(BWDropBoxStorage, self).modified_time(name)

    def accessed_time(self, name):
        return super(BWDropBoxStorage, self).accessed_time(name)

    def url(self, name):
        return super(BWDropBoxStorage, self).url(name)

    def _open(self, name, mode='rb'):
        return super(BWDropBoxStorage, self)._open(name, mode)

    def _save(self, name, content):
        return super(BWDropBoxStorage, self)._save(name, content)
