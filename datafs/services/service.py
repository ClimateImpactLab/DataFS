
from __future__ import absolute_import

import os
import fs.utils
import fs.path
from fs.osfs import OSFS


class DataService(object):

    def __init__(self, fs):
        self.fs = fs

    def __repr__(self):
        return "<{}:{} object at {}>".format(
            self.__class__.__name__, self.fs.__class__.__name__, hex(id(self)))

    def upload(self, filepath, service_path, remove=False):
        '''
        "Upload" a file to a service

        This copies a file from the local filesystem into the ``DataService``'s
        filesystem. If ``remove==True``, the file is moved rather than copied.

        If ``filepath`` and ``service_path`` paths are the same, ``upload``
        deletes the file if ``remove==True`` and returns.

        Parameters
        ----------
        filepath : str
            Relative or absolute path to the file to be uploaded on the user's
            filesystem

        service_path: str
            Path to the destination for the file on the ``DataService``'s
            filesystem

        remove : bool
            If true, the file is moved rather than copied
        '''

        local = OSFS(os.path.dirname(filepath))

        # Skip if source and dest are the same
        if self.fs.hassyspath(service_path) and (
            self.fs.getsyspath(service_path) == local.getsyspath(
                os.path.basename(filepath))):

            if remove:
                os.remove(filepath)

            return

        if not self.fs.isdir(fs.path.dirname(service_path)):
            self.fs.makedir(
                fs.path.dirname(service_path),
                recursive=True,
                allow_recreate=True)

        if remove:
            fs.utils.movefile(
                local,
                os.path.basename(filepath),
                self.fs,
                service_path)

        else:
            fs.utils.copyfile(
                local,
                os.path.basename(filepath),
                self.fs,
                service_path)
