
from __future__ import absolute_import

import os
import fs.utils
from fs.osfs import OSFS
from fs.base import FS

from datafs.core.data_file import DataFile

class DataService(object):

    def __init__(self, fs, api=None):
        self.fs = fs
        self.api = api

    def get_datafile(self, archive_name, version_id, path):
        '''
        Retrieve a :py:class:`~datafs.core.data_file.DataFile` object

        Parameters
        ----------
        path : str
            path to the requested file, relative to the service root

        Returns
        -------
        datafile : object
            :py:class:`~datafs.core.data_file.DataFile` object
        
        '''

        return DataFile(self.api, archive_name, version_id, self.fs, path)

    def upload(self, filepath, path):
        '''

        Returns
        -------
        response : dict
            location of the object and other metadata

        '''

        current_fs = OSFS(os.path.dirname(filepath))
        current_path = os.path.basename(filepath)

        target_name = path

        self.fs.makedir(fs.path.dirname(target_name), recursive=True, allow_recreate=True)
        fs.utils.copyfile(current_fs, current_path, self.fs, target_name)

