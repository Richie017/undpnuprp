__author__ = 'ActiveHigh'

import os
import zipfile


class ArchiveManager(object):
    @staticmethod
    def zip_dir(src, dst):
        zf = zipfile.ZipFile("%s.zip" % (dst), "w")
        abs_src = os.path.abspath(src)
        for dirname, subdirs, files in os.walk(src):
            for filename in files:
                absname = os.path.abspath(os.path.join(dirname, filename))
                arcname = absname[len(abs_src) + 1:]
                zf.write(absname, arcname)
        zf.close()

    @staticmethod
    def zip_files(files, dst):
        zf = zipfile.ZipFile("%s.zip" % (dst), "w")
        for filename in files:
            zf.write(filename[0], filename[1])
        zf.close()