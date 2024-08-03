import os
import time
from datetime import datetime
from tempfile import gettempdir

from dbbackup.settings import STORAGE_OPTIONS
from dbbackup.utils import bytes_to_str

from blackwidow.dbmediabackup.utils.storages.dropbox import BWDropBoxStorage

__author__ = "Ziaul Haque"


class BWDownloader(object):
    @classmethod
    def storage_client(cls):
        _client = BWDropBoxStorage(**STORAGE_OPTIONS)
        return _client

    @classmethod
    def download_file(cls, filename, chunk_size=4 * 1024 * 1024):
        start_time = datetime.now()

        temp_dir = gettempdir()
        temp_file = os.path.join(temp_dir, filename)
        storage_client = cls.storage_client()
        f = storage_client.open(filename)
        total_size = storage_client.size(filename)
        start = time.perf_counter()
        downloaded = 0
        with f:
            with open(temp_file, 'wb') as output:
                while True:
                    chunk = f.read(chunk_size)
                    downloaded += len(chunk)
                    _speed = downloaded / (time.perf_counter() - start)
                    print('%.2f' % (downloaded / total_size * 100), '% speed: ', bytes_to_str(_speed))
                    if not chunk:
                        break
                    output.write(chunk)
        finish_time = datetime.now()
        print('Escaped Time:%s' % (finish_time - start_time).total_seconds())
        return output.name

    @classmethod
    def delete_file(cls, file_path):
        import os
        try:
            os.remove(file_path)
        except OSError:
            pass
