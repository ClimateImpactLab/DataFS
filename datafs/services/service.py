
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

    def upload(self, filepath, service_path):
        local = OSFS(os.path.dirname(filepath))
        fs.utils.copyfile(local, os.path.basename(filepath), self.fs, service_path)



def CachingService(DataService):
    def cache(self, authority, service_path):
        fs.utils.copyfile(authority.fs, service_path, self.fs, service_path, overwrite=True)